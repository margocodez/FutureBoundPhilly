import os
import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_sub TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    api_token_hash TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'in_progress',
    messages TEXT NOT NULL DEFAULT '[]',
    answers TEXT NOT NULL DEFAULT '{}',
    test_score_source TEXT NOT NULL DEFAULT 'student_estimate',
    model TEXT,
    probability REAL,
    risk_score INTEGER,
    risk_category TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS student_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    stage TEXT NOT NULL DEFAULT 'deciding',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE IF NOT EXISTS stage_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    stage TEXT NOT NULL,
    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    task_id TEXT,
    title TEXT NOT NULL,
    stage TEXT NOT NULL,
    due_date TEXT,
    status TEXT NOT NULL DEFAULT 'todo',
    completed_at TEXT,
    source TEXT NOT NULL DEFAULT 'template',
    UNIQUE (user_id, task_id)
);

CREATE TABLE IF NOT EXISTS conversation_messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    with sqlite3.connect(app.config["DATABASE"]) as conn:
        conn.executescript(SCHEMA)
    app.teardown_appcontext(close_db)
