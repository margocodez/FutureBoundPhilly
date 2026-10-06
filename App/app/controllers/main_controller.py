from flask import Blueprint, g, redirect, render_template, request, url_for

from app.controllers.auth_controller import login_required
from app.models import Interview, Student

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if g.user is None:
        return render_template("login.html")
    interview = Interview.latest_for_user(g.user.id)
    if interview and interview.is_complete:
        return redirect(url_for("interview.checklist"))
    return redirect(url_for("interview.interview"))


@main_bp.route("/developer")
@login_required
def developer():
    return render_template("api.html", fields=Student.field_names(), new_token=None,
                           base_url=request.host_url.rstrip("/"))


@main_bp.route("/token", methods=["POST"])
@login_required
def generate_token():
    new_token = g.user.regenerate_api_token()
    return render_template("api.html", fields=Student.field_names(), new_token=new_token,
                           base_url=request.host_url.rstrip("/"))
