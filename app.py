# app.py
from flask import Flask, request, jsonify, render_template
from flask import Blueprint, render_template, request, flash, jsonify

views = Blueprint('views',__name__)

app = Flask(__name__)

# Store schedules (dictionary)
# schedules = {
#     "Monday": [],
#     "Tuesday": [],
#     "Wednesday": [],
#     "Thursday": [],
#     "Friday": []
# }


# Constants for the scheduling system
NUM_DAYS = 5  # Monday to Friday
NUM_TIME_SLOTS = 20  # Number of specified time slots

# Initialize a 3D list to hold schedules
schedules_3d = [[[] for _ in range(NUM_TIME_SLOTS)] for _ in range(NUM_DAYS)]

# Mapping from day names to indices (in /view_schedules it is top to bottom)
day_to_index = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4
}



#sets home.html to / (root/start page)
@app.route('/')
def index():
    return render_template('home.html')


#grabs data from dropzones in home.html
@app.route('/schedules', methods=['GET'])
def get_schedules():
    return jsonify(schedules)

#posts data to 3d array
#NEED TO FIGURE OUT SYSTEM TO ALIGN CLASS SETS (TR 10:05-11:30 needs to be under TR)
@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.json
    day = data.get('day')
    time_slot_index = int(data.get('time_slot'))
    class_name = data.get('class')
    
    if day in day_to_index and 0 <= time_slot_index < NUM_TIME_SLOTS:
        day_index = day_to_index[day]
        schedules_3d[day_index][time_slot_index].append(class_name)
        return jsonify(success=True, schedule=schedules_3d)
    
    return jsonify(success=False, message="Invalid input")

#removes class from 3d array if class is dragged into trash-bin on home page
#Are we forcing users to always use trash bin to fix mistake or are we going to
#allow users to drag from one time slot to another directly?
@app.route('/remove_class', methods=['POST'])
def remove_class():
    data = request.json
    day = data.get('day')
    time_slot_index = int(data.get('time_slot'))
    class_name = data.get('class')

    if day in day_to_index and 0 <= time_slot_index < NUM_TIME_SLOTS:
        day_index = day_to_index[day]
        if class_name in schedules_3d[day_index][time_slot_index]:
            schedules_3d[day_index][time_slot_index].remove(class_name)
            return jsonify(success=True, schedule=schedules_3d)

    return jsonify(success=False, message="Class not found or invalid input")


#view 3d array using 127.0.0.1/view_schedules
@app.route('/view_schedules', methods=['GET'])
def view_schedules():
    return jsonify(schedules_3d)


if __name__ == '__main__':
    app.run(debug=True)
