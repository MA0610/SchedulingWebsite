# app.py
from flask import Flask, request, jsonify, render_template
from flask import Blueprint, render_template, request, flash, jsonify

views = Blueprint('views',__name__)

app = Flask(__name__)

# Store schedules
schedules = {
    "Monday": [],
    "Tuesday": [],
    "Wednesday": [],
    "Thursday": [],
    "Friday": []
}





#go here to check if values are being uploaded
@app.route('/view_schedules', methods=['GET'])
def view_schedules():
    return jsonify(schedules)



@app.route('/')
def index():
    return render_template('home.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.json
    day = data.get('day')
    class_name = data.get('class')
    
    if day in schedules:
        schedules[day].append(class_name)
        return jsonify(success=True, schedule=schedules[day])
    return jsonify(success=False)

@app.route('/schedules', methods=['GET'])
def get_schedules():
    return jsonify(schedules)



@app.route('/remove_class', methods=['POST'])
def remove_class():
    data = request.json
    day = data.get('day')
    class_name = data.get('class')

    if day in schedules and class_name in schedules[day]:
        schedules[day].remove(class_name)
        return jsonify(success=True, schedule=schedules[day])
    
    return jsonify(success=False, message="Class not found")



if __name__ == '__main__':
    app.run(debug=True)
