from flask import Blueprint, g, redirect, render_template, request, url_for, current_app

from app.controllers.auth_controller import login_required
from app.models import Interview, Student

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if g.user is None:
        button_url = url_for("auth.login")
        button_text = "Sign in with Google"
    elif g.user.email.lower() in current_app.config["STAFF_EMAILS"]:
        button_url = url_for("staff.dashboard")
        button_text = "Open staff dashboard"
    else:
        interview = Interview.latest_for_user(g.user.id)
        if interview and interview.is_complete:
            button_url = url_for("interview.checklist")
            button_text = "Go to my checklist"
        else:
            button_url = url_for("interview.interview")
            button_text = "Start with Atlas"
    return render_template("home.html", button_url=button_url, button_text=button_text)


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
