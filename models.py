from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    time_slots = db.relationship('TimeSlot', backref='day', lazy=True)

class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    classes = db.relationship('ScheduledClass', backref='time_slot', lazy=True)

class ScheduledClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    professor_name = db.Column(db.String(100), nullable=False)
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slot.id'), nullable=False)
    day_blocks = db.Column(db.String(100), nullable=True)
    class_section = db.Column(db.String(10), nullable = True)
