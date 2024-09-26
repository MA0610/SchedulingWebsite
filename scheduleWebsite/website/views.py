from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Schedule
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        class1 = request.form.get('class1')#Gets the note from the HTML 

        if len(class1) < 1:
            flash('Class name is too short!', category='error') 
        else:
            new_class = Schedule(data=class1, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_class) #adding the note to the database 
            db.session.commit()
            flash('Class added!', category='success')

    return render_template("home.html", user=current_user)


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