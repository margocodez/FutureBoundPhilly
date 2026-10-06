import os

from dotenv import load_dotenv

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(APP_ROOT, ".env"))

# Trained artifacts (.pt, .pkl) live next to the training scripts in FBP_NN/.
ARTIFACT_DIR = os.environ.get(
    "ARTIFACT_DIR",
    os.path.abspath(os.path.join(APP_ROOT, "..", "FBP_NN")),
)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    ARTIFACT_DIR = ARTIFACT_DIR
    DATABASE = os.environ.get("DATABASE", os.path.join(APP_ROOT, "instance", "app.db"))

    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
