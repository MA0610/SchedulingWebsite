from flask import Flask, request, jsonify, render_template, Blueprint  
from typing import Optional, List
from models import db, Day, TimeSlot, ScheduledClass

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedules.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()  # Creates the database tables

views = Blueprint('views', __name__)

# Constants for the array scheduling system
NUM_DAYS = 5  # Monday to Friday
NUM_TIME_SLOTS = 20  # Number of specified time slots

# Initialize a 3D list to hold schedules
schedules_3d = [[[] for _ in range(NUM_TIME_SLOTS)] for _ in range(NUM_DAYS)]

# Mapping from day names to indices
day_to_index = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4
}

# Sets home.html to / (root/start page)
@app.route('/')
def index():
    return render_template('home.html')

# Grabs data from dropzones in home.html
@app.route('/schedules', methods=['GET'])
def get_schedules():
    return jsonify(schedules_3d)

# Posts data to database
@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.json
    new_schedule = data.get('schedule')
    dayBlocks = data.get('set')  # This could be a single block or a list of blocks
    timeBlock = data.get('time')
    profName = data.get('professor')

    if new_schedule and len(new_schedule) == NUM_DAYS and all(len(day) == NUM_TIME_SLOTS for day in new_schedule):
        for day_index, day in enumerate(new_schedule):
            for time_slot_index, class_names in enumerate(day):
                if class_names:  # If there are classes to add
                    day_name = list(day_to_index.keys())[day_index]
                    day_obj = Day.query.filter_by(name=day_name).first() or Day(name=day_name)
                    db.session.add(day_obj)
                    db.session.commit()

                    time_slot_obj = TimeSlot.query.filter_by(day_id=day_obj.id, time=timeBlock).first()
                    if not time_slot_obj:
                        time_slot_obj = TimeSlot(day_id=day_obj.id, time=timeBlock)
                        db.session.add(time_slot_obj)
                        db.session.commit()

                    for class_name in class_names:
                        class_obj = ScheduledClass.query.filter_by(name=class_name, time_slot_id=time_slot_obj.id).first()
                        if not class_obj:
                            class_obj = ScheduledClass(
                                name=class_name,
                                professor_name=profName,
                                time_slot_id=time_slot_obj.id,
                                day_blocks="".join(dayBlocks)  # Store dayBlocks
                            )
                            db.session.add(class_obj)

                    db.session.commit()

        # Copy classes to paired days based on dayBlocks
        copy_classes(dayBlocks)

        return jsonify(success=True, message="Schedule added successfully")

    return jsonify(success=False, message="Invalid input")

def copy_classes(dayBlocks):
    day_pairs = {
        'MW': ['Monday', 'Wednesday'],
        'MF': ['Monday', 'Friday'],
        'TR': ['Tuesday', 'Thursday'],
        'MWF': ['Monday', 'Wednesday', 'Friday'],
        'M-F': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }

    for pair in day_pairs:
        if pair not in dayBlocks:
            continue

        days = day_pairs[pair]

        for source_day in days:
            source_day_obj = Day.query.filter_by(name=source_day).first()
            if not source_day_obj:
                continue  # Skip if source day doesn't exist

            # Get time slots for the source day
            time_slots = TimeSlot.query.filter_by(day_id=source_day_obj.id).all()
            for time_slot in time_slots:
                class_names_with_professors = [
                    (scheduled_class.name, scheduled_class.professor_name, scheduled_class.day_blocks)
                    for scheduled_class in ScheduledClass.query.filter_by(time_slot_id=time_slot.id).all()
                ]

                for target_day in days:
                    if target_day == source_day:
                        continue  # Skip copying to the same day

                    target_day_obj = Day.query.filter_by(name=target_day).first()
                    if not target_day_obj:
                        target_day_obj = Day(name=target_day)
                        db.session.add(target_day_obj)
                        db.session.commit()  # Ensure target Day is saved

                    target_time_slot = TimeSlot.query.filter_by(day_id=target_day_obj.id, time=time_slot.time).first()
                    if not target_time_slot:
                        target_time_slot = TimeSlot(day_id=target_day_obj.id, time=time_slot.time)
                        db.session.add(target_time_slot)

                    for class_name, professor_name, day_blocks in class_names_with_professors:
                        if not ScheduledClass.query.filter_by(name=class_name, time_slot_id=target_time_slot.id).first():
                            new_class = ScheduledClass(
                                name=class_name,
                                professor_name=professor_name,
                                time_slot_id=target_time_slot.id,
                                day_blocks=day_blocks  # Copy day_blocks
                            )
                            db.session.add(new_class)

    db.session.commit()  # Commit changes after copying classes

@app.route('/clear_database', methods=['POST']) #TEMP
def clear_database():
    try:
        # Clear all scheduled classes
        ScheduledClass.query.delete()
        # Clear all time slots
        TimeSlot.query.delete()
        # Clear all days
        Day.query.delete()

        db.session.commit()  # Commit the changes to the database

        return jsonify(success=True, message="Database cleared successfully.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify(success=False, message="An error occurred while clearing the database.", error=str(e))


@app.route('/test', methods=['GET'])
def test():
    schedules = {}
    days = Day.query.all()

    for day in days:
        day_data = {
            "name": day.name,
            "time_slots": []
        }
        time_slots = TimeSlot.query.filter_by(day_id=day.id).all()

        for time_slot in time_slots:
            class_info = []
            scheduled_classes = ScheduledClass.query.filter_by(time_slot_id=time_slot.id).all()

            for scheduled_class in scheduled_classes:
                class_info.append({
                    "class_name": scheduled_class.name,
                    "professor_name": scheduled_class.professor_name,
                    "day_blocks": scheduled_class.day_blocks  # Include day_blocks
                })

            day_data["time_slots"].append({
                "time": time_slot.time,
                "classes": class_info
            })

        schedules[day.name] = day_data

    return jsonify(schedules)


@app.route('/remove_class_db', methods=['POST'])
def remove_class_db():
    data = request.json
    class_name = data.get('class_name')
    professor_name = data.get('professor_name')
    time_slot_time = data.get('time_slot_time')  # This should match the time string

    print(f"Removing class: {class_name}, Professor: {professor_name}, Time Slot: {time_slot_time}")

    try:
        # Find all scheduled classes with the same name and professor
        scheduled_classes = ScheduledClass.query.filter_by(
            name=class_name,
            professor_name=professor_name
        ).all()

        if scheduled_classes:
            # Remove each scheduled class
            for scheduled_class in scheduled_classes:
                db.session.delete(scheduled_class)

                # Check if there are other classes associated with this time slot
                remaining_classes = ScheduledClass.query.filter_by(time_slot_id=scheduled_class.time_slot_id).all()

                # If no other classes exist for this time slot, delete the time slot
                if not remaining_classes:
                    time_slot = TimeSlot.query.get(scheduled_class.time_slot_id)
                    if time_slot:
                        db.session.delete(time_slot)

            db.session.commit()  # Commit changes
            return jsonify(success=True, message="Class and associated time slots removed successfully.")
        else:
            return jsonify(success=False, message="Class not found.")

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message="An error occurred while removing the class.", error=str(e))


@app.route('/display_schedules', methods=['GET'])
def display_schedules():
    schedules = {}
    days = Day.query.all()

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    for day_name in day_order:
        day_obj = Day.query.filter_by(name=day_name).first()
        if day_obj:
            day_data = {
                "name": day_name,
                "time_slots": []
            }
            time_slots = TimeSlot.query.filter_by(day_id=day_obj.id).all()

            for time_slot in time_slots:
                class_info = []
                scheduled_classes = ScheduledClass.query.filter_by(time_slot_id=time_slot.id).all()

                for scheduled_class in scheduled_classes:
                    class_info.append({
                        "class_name": scheduled_class.name,
                        "professor_name": scheduled_class.professor_name,
                        "day_blocks": scheduled_class.day_blocks  # Include day_blocks here
                    })

                day_data["time_slots"].append({
                    "time": time_slot.time,
                    "classes": class_info
                })

            schedules[day_name] = day_data

    return render_template('schedules.html', schedules=schedules)

"""Everything below this line is meant to detect potential class conflicts"""
#Storing in globally held dictionary for now
class_conflicts = {}

def record_conflict(class_name1:str, class_name2: str):
    #Records conflicts between two classes in dictionary
    if class_name1 not in class_conflicts:
        class_conflicts[class_naame_1] = set()
    if class_name2 not in class_conflicts:
        class_conflicts[class_name2] = set()
    
    class_conflicts[class_name1].add(class_name2)
    class_conflicts[class_name2].add(class_name1)

def find_conflicts(class_name:str) -> Optional[List[str]]:
    #Finds all conflicts for a given class when passed
    if class_name in class_conflicts:
        return list(class_conflicts.get(class_name, []))
    else:
        return None

def find_all_conflicts(classList:List[str]) -> List[str]:
    conflicts = set()
    for class_name in classList:
        conflicts = find_conflicts(class_name)
        for conflict in conflicts:
            potential_conflicts.add(f"{class_name} conflicts with {conflict}")
    return list(potential_conflicts)



if __name__ == '__main__':
    app.run(debug=True)
