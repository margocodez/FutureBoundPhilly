from flask import Blueprint, current_app, render_template, url_for, redirect, request, abort, flash
from app.controllers.auth_controller import staff_required
from app.models.staff import Staff
from app.models.mentors import Mentor
from app.models.reminders import Reminder

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/staff")
@staff_required
def dashboard():
    priority_students = Staff.priority_list()
    for student in priority_students[:]:
        if student["email"] in current_app.config["STAFF_EMAILS"]:
            priority_students.remove(student)
    return render_template("staff.html", students=priority_students)

@staff_bp.route("/staff/assign/<int:user_id>", methods=["POST"])
@staff_required
def assign_mentor(user_id):
    mentor_email = request.form.get("mentor_email", "")
    if mentor_email not in current_app.config["MENTOR_EMAILS"]:
        abort(400)
    Mentor.assign(user_id, mentor_email)
    return redirect(url_for("staff.dashboard"))

@staff_bp.route("/staff/reminders", methods=["POST"])
@staff_required
def send_reminders():
    sent = Reminder.send_all(current_app.config["REMINDER_DAYS_AHEAD"])
    if sent == 1:
        flash("Sent 1 reminder email.")
    else:
        flash(f"Sent {sent} reminder emails.")
    return redirect(url_for("staff.dashboard"))
