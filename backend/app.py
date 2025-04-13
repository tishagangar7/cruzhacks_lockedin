from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from filters.schedule import process_user_schedule
from filters.syllabus_processing import process_syllabus
# from routes.profile_routes import register_profile_routes
# from routes.preferences.preferences_main import preferences_bp
# import os

app = Flask(__name__)
CORS(app)
app.secret_key = "yoursecretkeyhere"

# DB Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

import os
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

db.init_app(app)

# Create DB
with app.app_context():
    db.create_all()


# from flask import Flask, request, jsonify
# from models import db, User

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdb.sqlite3'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

#---signup/login routes---
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already exists"}), 400

    # Create a new user
    user = User(email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    # Return success with the user_id
    return jsonify({
        "success": True,
        "message": "Signup successful",
        "user_id": user.id  # Include the user_id in the response
    })

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        # Store the user_id in the session
        session["user_id"] = user.id
        return jsonify({"success": True, "message": "Login successful", "user_id": user.id})
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401
    
@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        })
    else:
        return jsonify({"success": False, "message": "User not found"}), 404

# -------------------- PROFILE ROUTES --------------------
@app.route("/api/profile", methods=["POST"])
def update_profile():
    data = request.get_json()
    user_id = data.get("user_id")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    user.name = data.get("name")
    user.major = data.get("major")
    user.year = data.get("year")
    user.study_style = data.get("study_style")
    user.classes = ",".join(data.get("classes", []))  # Convert list to comma string

    db.session.commit()
    return jsonify({"success": True, "message": "Profile updated successfully!"})

# 
    # Save profile info...
# Register the preferences blueprint
# app.register_blueprint(preferences_bp, url_prefix='/preferences')
#-------schedule------------------

@app.route("/api/process-schedule", methods=["POST"])
def process_schedule():
    """
    API endpoint to process the user's schedule.
    """
    try:
        # Get the user ID from the session (assuming user authentication is implemented)
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        # Get the schedule data from the request
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        # Process the schedule using the function from schedule.py
        result = process_user_schedule(data)

        # If processing is successful, save the valid schedule to the database
        if result["success"]:
            # Save the valid slots to the database (optional)
            save_schedule_to_db(user_id, result["valid_slots"], data.get("duration", 1))

        # Return the result to the frontend
        return jsonify(result)

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
    
from models import db, Filter
import json

def save_schedule_to_db(user_id, valid_slots, duration):
    """
    Save the valid schedule to the database.
    :param user_id: ID of the user
    :param valid_slots: Valid time slots
    :param duration: Duration of the time slots
    """
    # Convert the valid slots dictionary to a JSON string
    schedule_json = json.dumps(valid_slots)

    # Check if the user already has a schedule saved
    existing_filter = Filter.query.filter_by(user_id=user_id).first()
    if existing_filter:
        # Update the existing schedule
        existing_filter.schedule = schedule_json
        existing_filter.duration = duration
    else:
        # Create a new schedule entry
        new_filter = Filter(user_id=user_id, schedule=schedule_json, duration=duration)
        db.session.add(new_filter)

    db.session.commit()

#-------------------- get schedules --------------------
@app.route("/api/get-schedule", methods=["GET"])
def get_schedule():
    """
    API endpoint to retrieve the user's saved schedule.
    """
    try:
        # Get the user ID from the session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        # Retrieve the schedule from the database
        existing_filter = Filter.query.filter_by(user_id=user_id).first()
        if existing_filter and existing_filter.schedule:
            schedule = json.loads(existing_filter.schedule)
            return jsonify({"success": True, "schedule": schedule, "duration": existing_filter.duration})

        return jsonify({"success": False, "message": "No schedule found"}), 404

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"success": False, "message": "An error occurred", "error": str(e)}), 500
def apply_schedule_filter(schedule, schedule_filter):
    """
    Filter the schedule based on the provided criteria.
    :param schedule: The user's schedule (dict).
    :param schedule_filter: The filter criteria (dict).
    :return: Filtered schedule (dict).
    """
    filtered_schedule = {}
    for day, slots in schedule.items():
        filtered_slots = []
        for slot in slots:
            # Check if the slot matches the filter criteria
            if "category" in schedule_filter and slot["category"].lower() != schedule_filter["category"].lower():
                continue
            if "time" in schedule_filter and schedule_filter["time"] not in slot["time"]:
                continue
            filtered_slots.append(slot)
        if filtered_slots:
            filtered_schedule[day] = filtered_slots
    return filtered_schedule

@app.route("/api/upload-syllabus", methods=["POST"])
def upload_syllabus():
    try:
        
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        if "file" not in request.files:
            return jsonify({"success": False, "message": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "message": "No file selected"}), 400

        filename = secure_filename(file.filename)
        syllabus_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(syllabus_path)

        # Process the syllabus and save keywords to the database
        from filters.syllabus_processing import process_syllabus
        result = process_syllabus(syllabus_path, user_id, filename)

        return jsonify(result)
    
    except Exception as e:
        print(f"Error uploading syllabus: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/filters", methods=["POST"])
def apply_filters():
    """
    API endpoint to apply filters and retrieve data.
    If no filters are provided, return the entire study group database.
    """
    try:
        # Get the user ID from the session
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        # Get the filter criteria from the request
        filters = request.get_json()
        if not filters:
            # No filters provided, return all data
            return jsonify({
                "success": True,
                "message": "No filters provided. Returning all data.",
                "data": get_all_study_group_data()
            })

        # Initialize the response
        response = {}

        # Apply schedule filters
        if "schedule" in filters:
            schedule_filter = filters["schedule"]
            existing_filter = Filter.query.filter_by(user_id=user_id).first()
            if existing_filter and existing_filter.schedule:
                schedule = json.loads(existing_filter.schedule)
                filtered_schedule = apply_schedule_filter(schedule, schedule_filter)
                response["schedule"] = filtered_schedule

        # Apply keyword/topic filters
        if "keywords" in filters:
            keyword_filter = filters["keywords"]
            keywords = Keyword.query.filter_by(user_id=user_id).all()
            filtered_keywords = [k.keyword for k in keywords if keyword_filter.lower() in k.keyword.lower()]
            response["keywords"] = filtered_keywords

        # Apply class filters
        if "classes" in filters:
            class_filter = filters["classes"]
            user = User.query.get(user_id)
            if user and user.classes:
                user_classes = user.classes.split(",")
                filtered_classes = [c for c in user_classes if class_filter.lower() in c.lower()]
                response["classes"] = filtered_classes

        return jsonify({"success": True, "filters": response})

    except Exception as e:
        print(f"Error applying filters: {e}")
        return jsonify({"success": False, "message": str(e)}), 500    

@app.route("/api/get-user-classes", methods=["GET"])
def get_user_classes():
    """
    API endpoint to fetch the user's classes.
    """
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        user = User.query.get(user_id)
        if not user or not user.classes:
            return jsonify({"success": False, "message": "No classes found"}), 404

        classes = user.classes.split(",")  # Assuming classes are stored as a comma-separated string
        return jsonify({"success": True, "classes": classes})

    except Exception as e:
        print(f"Error fetching user classes: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/filtered-groups", methods=["GET"])
def get_filtered_groups():
    try:
        conn = sqlite3.connect("study_groups.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_groups")
        rows = cursor.fetchall()

        groups = []
        for row in rows:
            location = row[6] or "Remote"
            
            # Choose image URL based on location
            if "McHenry" in location:
                image_url = "https://bora.co/wp-content/uploads/2015/12/bora_UCSC_McHenryLibrary_02.jpg"
            elif "Science" in location:
                image_url = "https://source.unsplash.com/400x300/?engineering,library"
            elif "Jacks" in location:
                image_url = "https://source.unsplash.com/400x300/?lounge,students"
            elif row[5] == "remote":
                image_url = "https://source.unsplash.com/400x300/?study,online"
            else:
                image_url = "https://source.unsplash.com/400x300/?books,students"

            groups.append({
                "group_id": row[0],
                "class_code": row[1],
                "subject_title": row[2],
                "topics": json.loads(row[3]),
                "time_blocks": json.loads(row[4]),
                "mode": row[5],
                "location": location,
                "group_size": row[7],
                "study_style": row[8],
                "description": row[9],
                "image_url": image_url
            })

        return jsonify(groups)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
