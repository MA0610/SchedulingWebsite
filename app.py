from flask import Flask, request, jsonify, render_template, Blueprint
from dotenv import dotenv_values
from typing import Optional, List
from models import Class
from pymongo import MongoClient
from pydantic import ValidationError

config = dotenv_values(".env")
views = Blueprint('views', __name__)

app = Flask(__name__)

# Constants for the scheduling system
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

# Posts data to 3D array
@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.json
    new_schedule = data.get('schedule')
    dayBlocks = data.get('set') #grabs dayPairs ex. MW
    timeBlock = data.get('time') #gets the time block ex. 10:05-11:30

    if new_schedule and len(new_schedule) == NUM_DAYS and all(len(day) == NUM_TIME_SLOTS for day in new_schedule):
        for day_index, day in enumerate(new_schedule):
            for time_slot_index, class_names in enumerate(day):
                if class_names:  # If there are classes to add
                    for class_name in class_names:
                        # Add the class to the main day
                        schedules_3d[day_index][time_slot_index].append(class_name)

                        if dayBlocks == 'MW':



                            # Copy to Monday and Wednesday
                            for target_day in [0, 2]:  # Monday and Wednesday
                                # for x in schedules_3d[target_day][time_slot_index]:
                                #     if(timeBlock == schedules_3d[target_day][x]):
                                        if class_name not in schedules_3d[target_day][time_slot_index]:
                                            schedules_3d[target_day][time_slot_index].append(class_name)
                        elif dayBlocks == 'MF':
                            # Copy to Monday and Friday
                            for target_day in [0, 4]:  # Monday and Friday
                                if class_name not in schedules_3d[target_day][time_slot_index]:
                                    schedules_3d[target_day][time_slot_index].append(class_name)
                        elif dayBlocks == 'MWF':
                            # Copy to Monday, Wednesday, and Friday
                            for target_day in [0, 2, 4]:  # Monday, Wednesday, and Friday
                                if class_name not in schedules_3d[target_day][time_slot_index]:
                                    schedules_3d[target_day][time_slot_index].append(class_name)
                        elif dayBlocks == 'TR':
                            # Copy to Tuesday and Thursday
                            for target_day in [1, 3]:  # Tuesday and Thursday
                                if class_name not in schedules_3d[target_day][time_slot_index]:
                                    schedules_3d[target_day][time_slot_index].append(class_name)
                        elif dayBlocks == 'M-F':
                            # Copy to all days (Monday through Friday)
                            for i in range(NUM_DAYS):
                                if class_name not in schedules_3d[i][time_slot_index]:
                                    schedules_3d[i][time_slot_index].append(class_name)

        return jsonify(success=True, schedule=schedules_3d)

    return jsonify(success=False, message="Invalid input")


# Removes class from 3D array if class is dragged into trash-bin on home page
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

# View 3D array using 127.0.0.1/view_schedules
@app.route('/view_schedule', methods=['GET'])
def view_schedules():
    return jsonify(schedules_3d)

@app.route('/display_schedules', methods=['GET'])
def display_schedules():
    return render_template('schedules.html', schedules=schedules_3d)





# ###
# client = MongoClient('mongodb://localhost:27017/')
# db = client['your_database']

# @app.get('/getAll')
# def getAll():
#     classTimes = db.classes.find({})
#     return jsonify({
#         "data": list(classTimes)
#     }), 200

# @app.post('/add')
# def add():
#     data = request.json
#     new_schedule = data.get('schedule') 
#     try:
#         # Validate incoming data with the Class model
#         new_class = Class(**data)
#         db.classes.insert_one(new_class.dict(by_alias=True))
#         return {
#             "message": "Class added"
#         }, 200
#     except ValidationError as e:
#         return jsonify({
#             "error": e.errors()
#         }), 400

# @app.delete('/delete/<class_name>')
# def delete(class_name):
#     result = db.classes.delete_one({"class_name": class_name})
#     if result.deleted_count > 0:
#         return {
#             "message": "Class deleted"
#         }, 200
#     else:
#         return {
#             "error": "Class not found"
#         }, 404

# # Additional route to update class info
# @app.put('/update/<class_name>')
# def update(class_name):
#     data = request.json
#     try:
#         # Validate incoming update data with the Class model
#         updated_class = Class(**data)
#         result = db.classes.update_one(
#             {"class_name": class_name},
#             {"$set": updated_class.dict(by_alias=True)}
#         )
#         if result.matched_count > 0:
#             return {
#                 "message": "Class updated"
#             }, 200
#         else:
#             return {
#                 "error": "Class not found"
#             }, 404
#     except ValidationError as e:
#         return jsonify({
#             "error": e.errors()
#         }), 400



# ###







if __name__ == '__main__':
    app.run(debug=True)
