from flask import Blueprint, current_app, g, jsonify, redirect, render_template, request, url_for, abort

from app.controllers.auth_controller import login_required
from app.models import Interview, atlas, get_predictor, StudentProfile, Checklist
from app.models.checklist import TASK_HELP
from app.models.enrollment import STAGES
from app.models.checklist import stage_summary

interview_bp = Blueprint("interview", __name__)


def _first_name():
    return (g.user.name or "").split(" ")[0]


@interview_bp.route("/interview")
@login_required
def interview():
    current = Interview.get_or_start(g.user.id)
    if current.is_complete:
        return redirect(url_for("interview.checklist"))
    return render_template("interview.html", greeting=atlas.greeting(_first_name()),
                           transcript=current.transcript())


@interview_bp.route("/interview/message", methods=["POST"])
@login_required
def message():
    data = request.get_json(silent=True) or {}
    text = str(data.get("message", "")).strip()
    if not text:
        return jsonify(error="Message is empty"), 400
    if len(text) > 2000:
        return jsonify(error="Message is too long"), 400

    current = Interview.get_or_start(g.user.id)
    if current.is_complete:
        return jsonify(replies=[], done=True, redirect=url_for("interview.checklist"))

    result = atlas.run_turn(current, text, _first_name())
    current.save()

    if result["done"]:
        current.complete(get_predictor(current_app.config["ARTIFACT_DIR"], "B"))
        Checklist.generate_for(g.user.id, current.answers)
        StudentProfile.update_stage(g.user.id)
        return jsonify(replies=result["replies"], done=True,
                       redirect=url_for("interview.checklist"))
    return jsonify(replies=result["replies"], done=False)


@interview_bp.route("/checklist")
@login_required
def checklist():
    rows = Checklist.for_user(g.user.id)
    if not rows:
        return redirect(url_for("interview.interview"))
    profile = StudentProfile.get(g.user.id)
    return render_template("checklist.html", tasks=rows, stage=profile.stage, stages=stage_summary(rows), help=TASK_HELP)

@interview_bp.route("/checklist/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    if not Checklist.toggle(g.user.id, task_id):
        abort(404)
    return redirect(url_for("interview.checklist"))
