from flask import Blueprint, render_template, request, jsonify

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
        "email"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "success": False,
                "message": f"{field} is required."
            }), 400

    return jsonify({
        "success": True,
        "message": "Student registration received successfully.",
        "data": data
    }), 200