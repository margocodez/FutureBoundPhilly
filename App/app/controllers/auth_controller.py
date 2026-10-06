from functools import wraps

from flask import Blueprint, abort, g, redirect, session, url_for

from app.extensions import oauth
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.before_app_request
def load_current_user():
    user_id = session.get("user_id")
    g.user = User.get(user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("main.index"))
        return view(*args, **kwargs)
    return wrapped


@auth_bp.route("/login")
def login():
    redirect_uri = url_for("auth.callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/auth/callback")
def callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo")
    if not userinfo or not userinfo.get("email_verified"):
        abort(403, "Google account email is not verified.")

    user = User.upsert_from_google(userinfo)
    session.clear()
    session["user_id"] = user.id
    return redirect(url_for("main.index"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("main.index"))
