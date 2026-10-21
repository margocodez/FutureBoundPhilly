from flask import Blueprint, current_app, g, jsonify, redirect, render_template, request, url_for, abort

from app.controllers.auth_controller import login_required
from app.models import Interview, atlas, get_predictor, StudentProfile, Checklist
from app.models.checklist import TASK_HELP
from app.models.enrollment import STAGES
from app.models.checklist import stage_summary
from app.models.conversation import Conversation

atlas_bp = Blueprint("atlas", __name__)

def _first_name():
    return (g.user.name or "").split(" ")[0]

@atlas_bp.route("/atlas")
@login_required
def chat():
    interview = Interview.latest_for_user(g.user.id)

    if not interview or interview.status != "complete":
        return redirect(url_for("interview.interview"))

    history = Conversation.recent_history(g.user.id, 50)
    tasks = Checklist.for_user(g.user.id)

    profile = StudentProfile.get(g.user.id)
    stage = profile.stage if profile else None

    next_task = next(
        (task for task in tasks if task["status"] != "done"),
        None
    )

    first_name = _first_name()

    return render_template(
        "atlas.html",
        transcript=history,
        tasks=tasks,
        stage=stage,
        next_task=next_task,
        first_name=first_name
    )


@atlas_bp.route("/atlas/message", methods=["POST"])
@login_required
def message():
    data = request.get_json(silent=True) or {}
    text = str(data.get("message", "")).strip()
    if not text:
        return jsonify(error="Message is empty"), 400
    if len(text) > 2000:
        return jsonify(error="Message is too long"), 400
    interview = Interview.latest_for_user(g.user.id)
    if not interview or not interview.is_complete:
        return jsonify(error="Interview is incomplete"), 400

    if Conversation.daily_message_count(g.user.id) >= current_app.config["ATLAS_DAILY_MESSAGE_CAP"]:
        return jsonify(error = "Your message limit has been reached for today. Please come back tomorrow for more assistance!"), 429
    history = Conversation.recent_history(g.user.id)
    rows = Checklist.for_user(g.user.id)
    stage = StudentProfile.get(g.user.id).stage
    context = atlas.checklist_context(stage, rows, interview.answers)

    result = atlas.support_reply(history, text, context, _first_name())

    if result["ok"]:
        Conversation.save_message(g.user.id, "student", text)
        Conversation.save_message(g.user.id, "atlas", result["reply"])

    return jsonify(replies=[result["reply"]], done = False)