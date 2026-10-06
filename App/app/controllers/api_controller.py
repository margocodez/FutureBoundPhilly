from functools import wraps

from flask import Blueprint, current_app, g, jsonify, request

from app.models import Student, User, get_predictor
from app.models.predictor import MODEL_SPECS

api_bp = Blueprint("api", __name__, url_prefix="/api")


def token_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        user = User.from_api_token(token) if scheme.lower() == "bearer" and token else None
        if user is None:
            return jsonify(error="Missing or invalid API token"), 401
        g.api_user = user
        return view(*args, **kwargs)
    return wrapped


@api_bp.route("/predict", methods=["POST"])
@token_required
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    model_key = str(data.get("model", "B")).upper()
    if model_key not in MODEL_SPECS:
        return jsonify(error=f"Unknown model '{model_key}'. Use 'A' or 'B'."), 400

    try:
        student = Student.from_dict(data)
    except ValueError as e:
        return jsonify(error=str(e)), 400

    predictor = get_predictor(current_app.config["ARTIFACT_DIR"], model_key)
    return jsonify(predictor.predict(student))
