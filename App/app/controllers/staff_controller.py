from flask import Blueprint, current_app, render_template
from app.controllers.auth_controller import staff_required
from app.models.staff import Staff

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/staff")
@staff_required
def dashboard():
    priority_students = Staff.priority_list()
    for student in priority_students[:]:
        if student["email"] in current_app.config["STAFF_EMAILS"]:
            priority_students.remove(student)
    return render_template("staff.html", students=priority_students)
