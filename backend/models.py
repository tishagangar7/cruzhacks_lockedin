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

class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mode = db.Column(db.String(20))  # 'in-person', 'zoom', 'google meet'
    available_times = db.Column(db.Text)  # maybe a JSON string of time blocks
    selected_class = db.Column(db.String(100))
    topics = db.Column(db.Text)  # comma-separated list or raw string
    syllabus_keywords = db.Column(db.Text)  # (if extracted via AI)

