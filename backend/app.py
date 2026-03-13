import json
import os
import sqlite3
from datetime import timedelta
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

try:
    from .filters.schedule import process_user_schedule
    from .filters.syllabus_processing import process_syllabus
    from .models import CreatedGroup, Filter, GroupSelection, Keyword, User, db
except ImportError:
    from filters.schedule import process_user_schedule
    from filters.syllabus_processing import process_syllabus
    from models import CreatedGroup, Filter, GroupSelection, Keyword, User, db

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
PICTURES_DIR = BASE_DIR.parent / "pictures"
TILEPICS_DIR = BASE_DIR.parent / "tilepics"
UPLOAD_DIR = BASE_DIR / "uploads"
STUDY_GROUPS_DB_PATH = BASE_DIR / "study_groups.db"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-only-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", f"sqlite:///{BASE_DIR / 'users.db'}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    days=int(os.getenv("SESSION_LIFETIME_DAYS", "30"))
)

CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
db.init_app(app)

with app.app_context():
    db.create_all()


def _json_or_empty(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []


def _load_study_groups():
    if not STUDY_GROUPS_DB_PATH.exists():
        return []

    conn = sqlite3.connect(str(STUDY_GROUPS_DB_PATH))
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_groups")
        rows = cursor.fetchall()
    finally:
        conn.close()
    return rows


def _group_image(location, mode):
    location = location or "Remote"
    if "McHenry" in location:
        return "https://bora.co/wp-content/uploads/2015/12/bora_UCSC_McHenryLibrary_02.jpg"
    if "Science" in location:
        return "https://source.unsplash.com/400x300/?engineering,library"
    if "Jacks" in location:
        return "https://source.unsplash.com/400x300/?lounge,students"
    if mode == "remote":
        return "https://source.unsplash.com/400x300/?study,online"
    return "https://source.unsplash.com/400x300/?books,students"


def _serialize_group(row):
    location = row[6] or "Remote"
    mode = row[5] or "remote"
    return {
        "group_id": row[0],
        "class_code": row[1],
        "subject_title": row[2],
        "topics": _json_or_empty(row[3]),
        "time_blocks": _json_or_empty(row[4]),
        "mode": mode,
        "location": location,
        "group_size": row[7],
        "study_style": row[8],
        "description": row[9],
        "image_url": _group_image(location, mode),
    }


def _group_lookup():
    return {group["group_id"]: group for group in (_serialize_group(row) for row in _load_study_groups())}


def _get_user_id():
    user_id = session.get("user_id")
    if user_id:
        return user_id
    raw_user_id = request.args.get("user_id")
    if raw_user_id and raw_user_id.isdigit():
        return int(raw_user_id)
    return None


def save_schedule_to_db(user_id, valid_slots, duration):
    schedule_json = json.dumps(valid_slots)
    existing_filter = Filter.query.filter_by(user_id=user_id).first()
    if existing_filter:
        existing_filter.schedule = schedule_json
        existing_filter.duration = duration
    else:
        db.session.add(Filter(user_id=user_id, schedule=schedule_json, duration=duration))
    db.session.commit()


def apply_schedule_filter(schedule, schedule_filter):
    filtered_schedule = {}
    for day, slots in schedule.items():
        filtered_slots = []
        for slot in slots:
            if "category" in schedule_filter and slot.get("category", "").lower() != schedule_filter["category"].lower():
                continue
            if "time" in schedule_filter and schedule_filter["time"] not in slot.get("time", ""):
                continue
            filtered_slots.append(slot)
        if filtered_slots:
            filtered_schedule[day] = filtered_slots
    return filtered_schedule


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def root():
    return send_from_directory(str(FRONTEND_DIR), "login.html")


@app.route("/pictures/<path:path>", methods=["GET"])
def serve_pictures(path):
    return send_from_directory(str(PICTURES_DIR), path)


@app.route("/tilepics/<path:path>", methods=["GET"])
def serve_tilepics(path):
    return send_from_directory(str(TILEPICS_DIR), path)


@app.route("/<path:path>", methods=["GET"])
def serve_frontend(path):
    if path.startswith("api/"):
        return jsonify({"success": False, "message": "Not found"}), 404
    file_path = FRONTEND_DIR / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(str(FRONTEND_DIR), path)
    return send_from_directory(str(FRONTEND_DIR), "login.html")


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already exists"}), 400

    user = User(email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True, "message": "Signup successful", "user_id": user.id})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    remember = bool(data.get("remember", False))

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    session.permanent = remember
    session["user_id"] = user.id
    return jsonify({"success": True, "message": "Login successful", "user_id": user.id})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out"})


@app.route("/api/me", methods=["GET"])
def me():
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 401
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify(
        {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "major": user.major,
                "year": user.year,
                "classes": [c.strip() for c in (user.classes or "").split(",") if c.strip()],
                "study_style": user.study_style,
            },
        }
    )


@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    return jsonify(
        {"success": True, "user": {"id": user.id, "name": user.name, "email": user.email}}
    )


@app.route("/api/profile", methods=["POST"])
def update_profile():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    user.name = data.get("name")
    user.major = data.get("major")
    user.year = data.get("year")
    user.study_style = data.get("study_style")
    user.classes = ",".join(data.get("classes", []))
    db.session.commit()
    return jsonify({"success": True, "message": "Profile updated successfully!"})


@app.route("/api/process-schedule", methods=["POST"])
def process_schedule():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        data = request.get_json(silent=True) or {}
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        result = process_user_schedule(data)
        if result.get("success"):
            save_schedule_to_db(user_id, result.get("valid_slots", {}), data.get("duration", 1))
        return jsonify(result)
    except Exception as exc:
        return jsonify({"success": False, "message": "An error occurred", "error": str(exc)}), 500


@app.route("/api/get-schedule", methods=["GET"])
def get_schedule():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        existing_filter = Filter.query.filter_by(user_id=user_id).first()
        if existing_filter and existing_filter.schedule:
            return jsonify(
                {
                    "success": True,
                    "schedule": json.loads(existing_filter.schedule),
                    "duration": existing_filter.duration,
                }
            )
        return jsonify({"success": False, "message": "No schedule found"}), 404
    except Exception as exc:
        return jsonify({"success": False, "message": "An error occurred", "error": str(exc)}), 500


@app.route("/api/upload-syllabus", methods=["POST"])
def upload_syllabus():
    try:
        user_id = _get_user_id()
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
        result = process_syllabus(syllabus_path, user_id, filename)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/filters", methods=["POST"])
def apply_filters():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        filters = request.get_json(silent=True) or {}
        groups = [_serialize_group(row) for row in _load_study_groups()]
        if not filters:
            return jsonify({"success": True, "groups": groups, "filters": {}})

        response = {}
        if "schedule" in filters:
            existing_filter = Filter.query.filter_by(user_id=user_id).first()
            if existing_filter and existing_filter.schedule:
                response["schedule"] = apply_schedule_filter(
                    json.loads(existing_filter.schedule), filters["schedule"]
                )

        if "keywords" in filters:
            keyword_filter = str(filters["keywords"]).strip().lower()
            keywords = Keyword.query.filter_by(user_id=user_id).all()
            response["keywords"] = [
                k.keyword for k in keywords if keyword_filter in (k.keyword or "").lower()
            ]
            if keyword_filter:
                groups = [
                    group
                    for group in groups
                    if any(keyword_filter in str(topic).lower() for topic in group.get("topics", []))
                ]

        if "classes" in filters:
            class_filter = str(filters["classes"]).strip().lower()
            user = db.session.get(User, user_id)
            if user and user.classes:
                response["classes"] = [
                    c for c in user.classes.split(",") if class_filter in c.lower()
                ]
            if class_filter:
                groups = [
                    group
                    for group in groups
                    if class_filter in str(group.get("class_code", "")).lower()
                ]

        mode_filter = str(filters.get("mode", "")).strip().lower()
        if mode_filter:
            groups = [
                group for group in groups if mode_filter == str(group.get("mode", "")).strip().lower()
            ]

        location_filter = str(filters.get("location", "")).strip().lower()
        if location_filter:
            groups = [
                group
                for group in groups
                if location_filter in str(group.get("location", "")).strip().lower()
            ]

        return jsonify({"success": True, "groups": groups, "filters": response})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/get-user-classes", methods=["GET"])
def get_user_classes():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        user = db.session.get(User, user_id)
        if not user or not user.classes:
            return jsonify({"success": False, "message": "No classes found"}), 404
        return jsonify(
            {"success": True, "classes": [c.strip() for c in user.classes.split(",") if c.strip()]}
        )
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/filtered-groups", methods=["GET"])
def get_filtered_groups():
    try:
        groups = [_serialize_group(row) for row in _load_study_groups()]
        class_code = request.args.get("class_code", "").strip().lower()
        mode = request.args.get("mode", "").strip().lower()
        location = request.args.get("location", "").strip().lower()
        topic = request.args.get("topic", "").strip().lower()

        if class_code:
            groups = [g for g in groups if class_code in str(g.get("class_code", "")).lower()]
        if mode:
            groups = [g for g in groups if mode == str(g.get("mode", "")).lower()]
        if location:
            groups = [g for g in groups if location in str(g.get("location", "")).lower()]
        if topic:
            groups = [g for g in groups if any(topic in str(t).lower() for t in g.get("topics", []))]

        return jsonify({"success": True, "groups": groups})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/selections", methods=["GET"])
def get_selections():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        selections = (
            GroupSelection.query.filter_by(user_id=user_id)
            .order_by(GroupSelection.created_at.desc())
            .all()
        )
        lookup = _group_lookup()
        selected_groups = []
        for selection in selections:
            group = lookup.get(selection.group_id)
            if not group:
                continue
            selected_groups.append(
                {
                    "selection_id": selection.id,
                    "selected_at": selection.created_at.isoformat(),
                    "group": group,
                }
            )

        return jsonify({"success": True, "selected_groups": selected_groups})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/selections", methods=["POST"])
def save_selection():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        payload = request.get_json(silent=True) or {}
        raw_group_id = payload.get("group_id")
        selected = bool(payload.get("selected", True))
        try:
            group_id = int(raw_group_id)
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "group_id must be an integer"}), 400

        existing = GroupSelection.query.filter_by(user_id=user_id, group_id=group_id).first()
        if selected and not existing:
            db.session.add(GroupSelection(user_id=user_id, group_id=group_id))
            db.session.commit()
        elif not selected and existing:
            db.session.delete(existing)
            db.session.commit()

        selected_ids = [
            row.group_id for row in GroupSelection.query.filter_by(user_id=user_id).all()
        ]
        return jsonify({"success": True, "selected_group_ids": selected_ids})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/created-groups", methods=["GET"])
def get_created_groups():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        rows = (
            CreatedGroup.query.filter_by(user_id=user_id)
            .order_by(CreatedGroup.created_at.desc())
            .all()
        )
        groups = [
            {
                "id": row.id,
                "class_code": row.class_code,
                "location": row.location,
                "topics": [t.strip() for t in (row.topics or "").split(",") if t.strip()],
                "time_block": row.time_block,
                "mode": row.mode or "in_person",
                "description": row.description or "",
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
        return jsonify({"success": True, "groups": groups})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/created-groups", methods=["POST"])
def create_group():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        data = request.get_json(silent=True) or {}
        class_code = str(data.get("class_code", "")).strip()
        location = str(data.get("location", "")).strip()
        topics = data.get("topics", [])
        mode = str(data.get("mode", "in_person")).strip() or "in_person"
        time_block = str(data.get("time_block", "")).strip()
        description = str(data.get("description", "")).strip()

        if not class_code or not location:
            return jsonify({"success": False, "message": "class_code and location are required"}), 400

        if isinstance(topics, list):
            topics_str = ", ".join([str(t).strip() for t in topics if str(t).strip()])
        else:
            topics_str = str(topics).strip()

        group = CreatedGroup(
            user_id=user_id,
            class_code=class_code,
            location=location,
            topics=topics_str,
            time_block=time_block,
            mode=mode,
            description=description,
        )
        db.session.add(group)
        db.session.commit()
        return jsonify({"success": True, "group_id": group.id})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/api/match-users", methods=["GET"])
def match_users():
    try:
        user_id = _get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        user_classes = {c.strip().lower() for c in (user.classes or "").split(",") if c.strip()}
        user_keywords = {
            k.keyword.strip().lower() for k in Keyword.query.filter_by(user_id=user_id).all() if k.keyword
        }
        user_style = (user.study_style or "").strip().lower()

        candidates = []
        for row in _load_study_groups():
            group = _serialize_group(row)
            score = 0

            if group["class_code"] and group["class_code"].strip().lower() in user_classes:
                score += 3
            if user_style and (group["study_style"] or "").strip().lower() == user_style:
                score += 2

            topic_matches = 0
            for topic in group["topics"]:
                if str(topic).strip().lower() in user_keywords:
                    topic_matches += 1
            score += min(topic_matches * 2, 6)

            if score > 0:
                candidates.append(
                    {
                        "match_score": score,
                        "group_id": group["group_id"],
                        "name": group["subject_title"] or group["class_code"],
                        "class_code": group["class_code"],
                        "topics": ", ".join(group["topics"]) if group["topics"] else "",
                        "mode": group["mode"],
                        "location": group["location"],
                        "image_url": group["image_url"],
                    }
                )

        candidates.sort(key=lambda item: item["match_score"], reverse=True)
        return jsonify({"success": True, "matches": candidates})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
