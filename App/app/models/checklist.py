import json, os
from datetime import date
from app.models.db import get_db

TASKS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.json")

with open(TASKS_PATH) as f:
    MASTER_TASKS = json.load(f)

def applies(task, answers):
    for field, allowed in task["applies_to"].items():
        if answers.get(field) not in allowed:
            return False
    return True

def is_done(task, answers):
    completion = task.get("done_if")
    if not completion:
        return False
    for field, allowed in task["done_if"].items():
        if answers.get(field) != allowed:
            return False
    return True

def due_date(task):
    month, day = task["due"].split("-")   # split task["due"], then int() each part
    month=int(month)
    day=int(day)
    today = date.today()
    if today < date(today.year, 8, 15):
        year = today.year
    else:
        year = today.year + 1
    return date(year, month, day).isoformat()

class Checklist:
    @classmethod
    def generate_for(cls, user_id, answers):
        conn = get_db()
        for task in MASTER_TASKS:
            if not applies(task, answers):
                continue
            status = "done" if is_done(task, answers) else "todo"
            conn.execute(
                "INSERT OR IGNORE INTO student_tasks (user_id, task_id, title, stage, due_date, status) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, task["id"], task["title"], task["stage"], due_date(task), status),
            )
        conn.execute("UPDATE student_tasks SET completed_at = CURRENT_TIMESTAMP "
                     "WHERE user_id = ? AND status = 'done' AND completed_at IS NULL", (user_id,))
        conn.commit()