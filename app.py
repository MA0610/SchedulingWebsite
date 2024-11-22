from flask import Flask, request, jsonify, render_template, Blueprint  
from typing import Optional, List
from models import db, Day, TimeSlot, ScheduledClass, Conflict
from sqlalchemy import or_


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
    sectionNumber = data.get('section')

    # Ensure the schedule has the correct format
    if new_schedule and len(new_schedule) == NUM_DAYS and all(len(day) == NUM_TIME_SLOTS for day in new_schedule):
        for day_index, day in enumerate(new_schedule):
            for time_slot_index, class_names in enumerate(day):
                if class_names:  # If there are classes to add
                    day_name = list(day_to_index.keys())[day_index]
                    day_obj = Day.query.filter_by(name=day_name).first()

                    # If Day doesn't exist, create it
                    if not day_obj:
                        day_obj = Day(name=day_name)
                        db.session.add(day_obj)
                        db.session.commit()  # Ensure day is committed first

                    # Get the corresponding time slot object for the day
                    time_slot_obj = TimeSlot.query.filter_by(day_id=day_obj.id, time=timeBlock).first()
                    if not time_slot_obj:
                        time_slot_obj = TimeSlot(day_id=day_obj.id, time=timeBlock)
                        db.session.add(time_slot_obj)
                        db.session.commit()  # Ensure time slot is committed first

                    # Do not clear all existing classes; only add new classes
                    for class_name in class_names:
                        # Ensure that a class with the same section does not already exist for this time slot
                        existing_class = ScheduledClass.query.filter_by(
                            name=class_name,
                            time_slot_id=time_slot_obj.id,
                            class_section=sectionNumber
                        ).first()

                        if not existing_class:  # Only add if class with same name and section does not exist
                            class_obj = ScheduledClass(
                                name=class_name,
                                professor_name=profName,
                                time_slot_id=time_slot_obj.id,
                                day_blocks="".join(dayBlocks),
                                class_section=sectionNumber
                            )
                            db.session.add(class_obj)

                    db.session.commit()  # Commit changes to the database after class addition

        # Now copy the classes to paired days based on dayBlocks
        copy_classes(dayBlocks, sectionNumber)

        return jsonify(success=True, message="Schedule added successfully")
    
    return jsonify(success=False, message="Invalid input")



def copy_classes(dayBlocks, sectionNumber):
    day_pairs = {
        'MW': ['Monday', 'Wednesday'],
        'MF': ['Monday', 'Friday'],
        'WF': ['Wednesday', 'Friday'],
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
                # Get all the scheduled classes for the current time slot on the source day
                class_names_with_professors = [
                    (scheduled_class.name, scheduled_class.professor_name, scheduled_class.class_section, scheduled_class.day_blocks)
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

                    for class_name, professor_name, class_section, day_blocks in class_names_with_professors:
                        # Ensure the class is copied only if the section matches
                        if class_section != sectionNumber:
                            continue  # Skip copying if the section doesn't match

                        # Check if the class already exists with the same name, section, and time slot on the target day
                        existing_class = ScheduledClass.query.filter_by(
                            name=class_name,
                            professor_name=professor_name,
                            time_slot_id=target_time_slot.id,
                            class_section=sectionNumber  # Ensure section number is the same
                        ).first()

                        # Only add the class if it doesn't already exist on the target day and time slot
                        if not existing_class:
                            new_class = ScheduledClass(
                                name=class_name,
                                professor_name=professor_name,
                                time_slot_id=target_time_slot.id,
                                day_blocks=day_blocks,
                                class_section=sectionNumber
                            )
                            db.session.add(new_class)

    db.session.commit()  # Commit changes after copying classes

@app.route('/class_conflicts')
def class_conflicts():
    all_classes = ScheduledClass.query.all()  # Retrieve all classes from the database
    conflicts = Conflict.query.all()
    
    # Create a set of tuples for quick lookup of existing conflicts
    conflict_pairs = set()
    for conflict in conflicts:
        class_1 = ScheduledClass.query.get(conflict.class_id)
        class_2 = ScheduledClass.query.get(conflict.conflict_class_id)
        
        # Make sure both classes exist
        if class_1 and class_2:
            conflict_pairs.add((class_1.name, class_2.name))  # Use class names, not IDs

    # Build a detailed class list with time slot and day data
    detailed_classes = []
    for scheduled_class in all_classes:
        time_slot = TimeSlot.query.get(scheduled_class.time_slot_id)
        day = Day.query.get(time_slot.day_id) if time_slot else None
        detailed_classes.append({
            "id": scheduled_class.id,
            "name": scheduled_class.name,
            "professor_name": scheduled_class.professor_name,
            "class_section": scheduled_class.class_section,
            "time_slot": time_slot.time if time_slot else "Unknown",
            "day": day.name if day else "Unknown"
        })

    return render_template('class_conflicts.html', all_classes=detailed_classes, conflict_pairs=conflict_pairs)


@app.route('/add_conflict', methods=['POST'])
def add_conflict():
    data = request.json
    class_id = data.get('class_id')
    conflict_class_id = data.get('conflict_class_id')

    if not class_id or not conflict_class_id:
        return jsonify(success=False, message="Both class IDs are required.")

    # Check for existing conflicts in either direction
    existing_conflict = Conflict.query.filter(
        or_(
            (Conflict.class_id == class_id) & (Conflict.conflict_class_id == conflict_class_id),
            (Conflict.class_id == conflict_class_id) & (Conflict.conflict_class_id == class_id)
        )
    ).first()

    if existing_conflict:
        return jsonify(success=False, message="This conflict already exists.")

    # Add the conflict
    conflict = Conflict(class_id=class_id, conflict_class_id=conflict_class_id)
    db.session.add(conflict)
    db.session.commit()
    return jsonify(success=True, message="Conflict marked successfully.")


@app.route('/remove_conflict', methods=['POST'])
def remove_conflict():
    data = request.json
    class_id = data.get('class_id')
    conflict_class_id = data.get('conflict_class_id')

    # Remove the conflict
    conflict = Conflict.query.filter_by(class_id=class_id, conflict_class_id=conflict_class_id).first()
    if conflict:
        db.session.delete(conflict)
        db.session.commit()
        return jsonify(success=True, message="Conflict removed successfully.")
    return jsonify(success=False, message="Conflict not found.")


@app.route('/clear_conflicts', methods=['POST'])
def clear_conflicts():
    try:
        # Delete all rows in the Conflict table
        Conflict.query.delete()
        db.session.commit()
        return jsonify(success=True, message="All conflicts cleared successfully.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify(success=False, message="An error occurred while clearing conflicts.", error=str(e))


@app.route('/detect_conflicts', methods=['GET'])
def detect_conflicts():
    conflicts = Conflict.query.all()
    detected_conflicts = []
    for conflict in conflicts:
        class_1 = ScheduledClass.query.get(conflict.class_id)
        class_2 = ScheduledClass.query.get(conflict.conflict_class_id)
        if class_1 and class_2:
            detected_conflicts.append({
                "class_1": class_1.name,
                "class_2": class_2.name
            })
    return jsonify(detected_conflicts=detected_conflicts)



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
                    "class_section": scheduled_class.class_section,  # Include class_section
                    "day_blocks": scheduled_class.day_blocks
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
    class_section = data.get('class_section')

    print(f"Removing class: {class_name}, Professor: {professor_name}, Time Slot: {time_slot_time}")

    try:
        # Find all scheduled classes with the same name and professor
        scheduled_classes = ScheduledClass.query.filter_by(
            name=class_name,
            professor_name=professor_name,
            class_section = class_section
            
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

    # Get all user-defined conflicts
    conflicts = Conflict.query.all()
    conflicting_class_ids = set()
    for conflict in conflicts:
        conflicting_class_ids.add(conflict.class_id)
        conflicting_class_ids.add(conflict.conflict_class_id)

    # Iterate through each day and fetch the related time slots and classes
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
                        "id": scheduled_class.id,  # Include the class ID for conflict checking
                        "class_name": scheduled_class.name,
                        "professor_name": scheduled_class.professor_name,
                        "class_section": scheduled_class.class_section,
                        "day_blocks": scheduled_class.day_blocks
                    })

                day_data["time_slots"].append({
                    "time": time_slot.time,
                    "classes": class_info
                })

            schedules[day_name] = day_data

    # Pass the schedules and conflicting_class_ids to the template
    return render_template('schedules.html', schedules=schedules, conflicting_class_ids=conflicting_class_ids)


if __name__ == '__main__':
    app.run(debug=True)
