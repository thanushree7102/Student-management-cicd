from flask import Blueprint, jsonify, request, render_template
from db import get_db_connection

records_bp = Blueprint("records", __name__)


@records_bp.route("/records")
def records_page():
    return render_template("records/records.html")


@records_bp.route("/api/students")
def get_students():
    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:
        query = """
            SELECT id, name, usn, department
            FROM students
            WHERE name LIKE %s
               OR usn LIKE %s
               OR department LIKE %s
            ORDER BY id
        """
        value = f"%{search}%"
        cursor.execute(query, (value, value, value))
    else:
        query = """
            SELECT id, name, usn, department
            FROM students
            ORDER BY id
        """
        cursor.execute(query)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(students)
