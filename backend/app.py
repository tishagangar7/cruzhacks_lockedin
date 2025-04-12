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
        return jsonify({"success": False, "message": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already exists!"}), 400

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Signup successful!",
        "user_id": user.id  
    })


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        return jsonify({"success": True, "message": "Login successful!", "user_id": user.id})

    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401


@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "major": user.major,
            "year": user.year,
            "study_style": user.study_style,
            "classes": user.classes.split(",") if user.classes else []
        }
    })

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

    # THIS IS WHAT YOU FORGOT:
    return jsonify({"success": True, "message": "Profile updated successfully!"})

@app.route("/api/profile/upload-image/<int:user_id>", methods=["POST"])
def upload_profile_image(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    if "image" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Optionally store the filename in user DB
    # user.profile_image = filename
    # db.session.commit()

    return jsonify({"success": True, "message": "Image uploaded successfully!"})

    # Save profile info...
# Register the preferences blueprint
# app.register_blueprint(preferences_bp, url_prefix='/preferences')

if __name__ == '__main__':
    app.run(debug=True)
