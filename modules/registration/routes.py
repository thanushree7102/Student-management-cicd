import sqlite3
from flask import Blueprint, render_template, request, jsonify

from create_database import DB_PATH


registration_bp = Blueprint(
    "registration",
    __name__,
    url_prefix="/registration"
)


@registration_bp.route("/", methods=["GET"])
def registration_page():
    return render_template("registration/registration.html")


@registration_bp.route("/register", methods=["POST"])
def register_student():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No registration data received."
        }), 400

    required_fields = [
        "name",
        "usn",
        "department"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "success": False,
                "message": f"{field} is required."
            }), 400

    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        query = """
            INSERT INTO students (
                name,
                usn,
                date_of_birth,
                gender,
                department,
                semester,
                section,
                admission_year,
                email,
                phone,
                address,
                parent_name,
                parent_phone
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            data.get("name"),
            data.get("usn"),
            data.get("date_of_birth"),
            data.get("gender"),
            data.get("department"),
            data.get("semester"),
            data.get("section"),
            data.get("admission_year"),
            data.get("email"),
            data.get("phone"),
            data.get("address"),
            data.get("parent_name"),
            data.get("parent_phone")
        )

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Student registered successfully."
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "message": "USN already exists."
        }), 409

    except sqlite3.Error as error:
        return jsonify({
            "success": False,
            "message": f"Database error: {error}"
        }), 500