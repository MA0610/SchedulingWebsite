from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Schedule
from . import db
import json
import numpy as np

views = Blueprint('views', __name__)

def test():
    print("TEST")

#x is num of rows (time slots on given day: ?)
#y is num of columns (number of days in week: 5)
#z is num of entries in array (lists: 1)
def create_3d_list(x,y,z):
    lst = []
    for i in range(x):
        lst_2d = []
        for j in range(y):
            lst_1d = []
            for k in range(z):
                lst_1d.append([])
            lst_2d.append(lst_1d)
        lst.append(lst_2d)
    return lst


schedule = create_3d_list(20,5,1)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        className = request.form.get('class')
        if(className=='Math 101'):
            schedule[0,0,0] = className
            flash('Logged in successfully!', category='success')

#HERE
    return render_template("home.html", user=current_user, test=test)


@views.route('/delete-note', methods=['POST'])
def delete_class():  
    class1 = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    classId = class1['classId']
    class1 = Schedule.query.get(classId)
    if class1:
        if class1.user_id == current_user.id:
            db.session.delete(class1)
            db.session.commit()

    return jsonify({})