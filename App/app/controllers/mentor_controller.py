from flask import Blueprint, current_app, render_template, redirect, url_for, abort, request, g
from app.controllers.auth_controller import login_required, mentor_required
from app.models.mentors import Mentor

mentor_bp = Blueprint("mentor", __name__)

@mentor_bp.route("/mentor")
@login_required
def request_page():
    request_row=Mentor.open_request(g.user.id)
    assignment=Mentor.assignment_for(g.user.id)
    return render_template("mentor.html", request_row=request_row, assignment=assignment)

@mentor_bp.route("/mentor", methods=["POST"])
@login_required
def submit():
    help_with = request.form.get("help_with", "").strip()[:1000]
    best_time = request.form.get("best_time", "").strip()[:100]
    if not help_with:
        abort(400)
    if not Mentor.open_request(g.user.id):
        Mentor.create_request(user_id = g.user.id, help_with = help_with, best_time = best_time)
    return redirect(url_for("mentor.request_page"))

@mentor_bp.route("/mentoring")
@mentor_required
def my_students():
    students = Mentor.students_for(g.user.email.lower())
    return render_template("mentoring.html", students=students)