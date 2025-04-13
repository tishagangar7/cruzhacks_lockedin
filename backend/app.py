from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
# from routes.profile_routes import register_profile_routes
# from routes.preferences.preferences_main import preferences_bp
# import os

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(debug=True)
