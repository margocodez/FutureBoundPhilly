"""Load the fictional sample students from data/sample_data.json.

Used on the hosted demo (SEED_SAMPLE_DATA=1) so the staff and mentor pages have
students to show. Every sample student has an @example.com email and a google_sub
starting with "sample-", so they can never be signed in to and are easy to remove.
"""
import json
import os
import sqlite3
from datetime import date, timedelta

SAMPLE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data.json")


def seed_sample_data(app):
    """Insert the sample students unless they are already in the database."""
    with open(SAMPLE_FILE) as f:
        students = json.load(f)["students"]
    mentors = sorted(app.config["MENTOR_EMAILS"])
    today = date.today()

    with sqlite3.connect(app.config["DATABASE"]) as conn:
        if conn.execute("SELECT 1 FROM users WHERE google_sub LIKE 'sample-%'").fetchone():
            return

        for i, s in enumerate(students):
            user_id = conn.execute(
                "INSERT INTO users (google_sub, email, name) VALUES (?, ?, ?)",
                (s["google_sub"], s["email"], s["name"]),
            ).lastrowid

            if s["stage"]:
                conn.execute("INSERT INTO student_profiles (user_id, stage) VALUES (?, ?)", (user_id, s["stage"]))
                conn.execute("INSERT INTO stage_history (user_id, stage) VALUES (?, ?)", (user_id, s["stage"]))

            interview = s["interview"]
            if interview:
                conn.execute(
                    """
                    INSERT INTO interviews (user_id, status, messages, answers, test_score_source,
                                            model, probability, risk_score, risk_category, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (user_id, interview["status"], interview["messages"], interview["answers"],
                     interview["test_score_source"], interview["model"], interview["probability"],
                     interview["risk_score"], interview["risk_category"]),
                )

            for task in s["tasks"]:
                due_date = task.get("due_date")
                if "due_in_days" in task:
                    due_date = (today + timedelta(days=task["due_in_days"])).isoformat()
                conn.execute(
                    """
                    INSERT INTO student_tasks (user_id, task_id, title, stage, due_date, status, completed_at, source)
                    VALUES (?, ?, ?, ?, ?, ?, CASE WHEN ? = 'done' THEN CURRENT_TIMESTAMP END, ?)
                    """,
                    (user_id, task["task_id"], task["title"], task["stage"], due_date,
                     task["status"], task["status"], task["source"]),
                )

            for request in s["mentor_requests"]:
                conn.execute(
                    "INSERT INTO mentor_requests (user_id, help_with, best_time, status) VALUES (?, ?, ?, ?)",
                    (user_id, request["help_with"], request["best_time"], request["status"]),
                )

            # Sample students point at whoever is in MENTOR_EMAILS on this server.
            if s["has_mentor"] and mentors:
                conn.execute(
                    "INSERT INTO mentor_assignments (user_id, mentor_email) VALUES (?, ?)",
                    (user_id, mentors[i % len(mentors)]),
                )
