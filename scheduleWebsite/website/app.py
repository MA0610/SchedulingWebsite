from flask import Flask

from flask import request

@app.get('/getAll')
def getAll():
    classTimes = db.classes.find({})
    return {
        "data": list(classTimes)
    }, 200

@app.post('/add')
def add():
    data = request.json
    db.classes.insert_one(data)
    return {
        "message": "Class added"
    }, 200

@app.delete('/delete/<class_name>')
def delete(class_name):
    db.classes.delete_one({"class_name": class_name})
    return {
        "message": "Class deleted"
    }, 200
