from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100))
    major = db.Column(db.String(100))
    year = db.Column(db.Integer)
    classes = db.Column(db.Text)  # comma-separated class codes
    study_style = db.Column(db.String(100))


class UserClass(db.Model):  # Optional: class mapping table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_code = db.Column(db.String(50), nullable=False)

class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.Text, nullable=True)  # JSON string for schedule
    duration = db.Column(db.Integer, nullable=True)  # Duration of the time slots

class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Link to the user
    syllabus_name = db.Column(db.String(255), nullable=False)  # Name of the syllabus file
    keyword = db.Column(db.String(255), nullable=False)  # Extracted keyword/topic

class StudyGroups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classname = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    topics = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)
