from flask import Flask, request, jsonify
from typing import Optional, List
from models import Class
from pymongo import MongoClient
from pydantic import ValidationError

app = Flask(__name__)

# MongoDB setup (assuming db is already initialized)
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']

@app.get('/getAll')
def getAll():
    classTimes = db.classes.find({})
    return jsonify({
        "data": list(classTimes)
    }), 200

@app.post('/add')
def add():
    data = request.json
    try:
        # Validate incoming data with the Class model
        new_class = Class(**data)
        db.classes.insert_one(new_class.dict(by_alias=True))
        return {
            "message": "Class added"
        }, 200
    except ValidationError as e:
        return jsonify({
            "error": e.errors()
        }), 400

@app.delete('/delete/<class_name>')
def delete(class_name):
    result = db.classes.delete_one({"class_name": class_name})
    if result.deleted_count > 0:
        return {
            "message": "Class deleted"
        }, 200
    else:
        return {
            "error": "Class not found"
        }, 404

# Additional route to update class info
@app.put('/update/<class_name>')
def update(class_name):
    data = request.json
    try:
        # Validate incoming update data with the Class model
        updated_class = Class(**data)
        result = db.classes.update_one(
            {"class_name": class_name},
            {"$set": updated_class.dict(by_alias=True)}
        )
        if result.matched_count > 0:
            return {
                "message": "Class updated"
            }, 200
        else:
            return {
                "error": "Class not found"
            }, 404
    except ValidationError as e:
        return jsonify({
            "error": e.errors()
        }), 400
