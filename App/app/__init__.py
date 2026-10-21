from flask import Flask

from app.config import Config
from app.extensions import oauth
from app.models import db
from datetime import date


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )
    app.config.from_object(config_class)

    @app.template_filter("nice_date")
    def nice_date(value):
        d = date.fromisoformat(value)
        return d.strftime("%b %d, %Y")

    db.init_app(app)
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    from app.controllers.api_controller import api_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.interview_controller import interview_bp
    from app.controllers.main_controller import main_bp
    from app.controllers.atlas_controller import atlas_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(atlas_bp)

    return app
