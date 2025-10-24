from . import db
from datetime import date
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    roll = db.Column(db.String(32), nullable=False, index=True)
    phone = db.Column(db.String(32), nullable=False)
    class_name = db.Column(db.String(32), nullable=False, index=True)
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), index=True, nullable=False)
    date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    present = db.Column(db.Boolean, nullable=False)
    student = db.relationship('Student', backref='attendances')
