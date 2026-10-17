import json, os
from datetime import date
from app.models.db import get_db
from app.models.interview import Interview
from app.models.student_profile import StudentProfile
from app.models.enrollment import STAGES

TASKS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.json")

with open(TASKS_PATH) as f:
    MASTER_TASKS = json.load(f)
    TASK_HELP = {t["id"]:t["help"] for t in MASTER_TASKS}

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

def stage_summary(rows):
    dic_list=[]
    for stage in STAGES:
        tasks=[]
        completed_count=0
        earliest_due = None
        overdue=0
        for s in rows:
            if s["stage"] == stage:
                tasks.append(s)
                if s["status"]=="done":
                    completed_count+=1
                else:
                    if earliest_due == None:
                        earliest_due=s["due_date"]
                    if date.today().isoformat() > s["due_date"]:
                        overdue+=1
        dic_list.append({"name":stage,
                        "tasks":tasks,
                        "done":completed_count,
                        "total":len(tasks),
                        "overdue":overdue,
                        "next_due":earliest_due})
    return dic_list

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
    @classmethod
    def for_user(cls, user_id):
        rows = get_db().execute("SELECT * FROM student_tasks where user_id = ? ORDER BY due_date", (user_id,)).fetchall()
        if not rows:
            interview = Interview.latest_for_user(user_id)
            if interview is None or not interview.is_complete:
                return []
            Checklist.generate_for(user_id, interview.answers)
            StudentProfile.update_stage(user_id)
            rows = get_db().execute("SELECT * FROM student_tasks where user_id = ? ORDER BY due_date", (user_id,)).fetchall()
        return rows

    @classmethod
    def toggle(cls, user_id, task_row_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM student_tasks WHERE id = ? AND user_id = ?",
                        (task_row_id, user_id)).fetchone()
        if row is None:
            return None
        if row["status"] == "todo":
            conn.execute("UPDATE student_tasks SET status = 'done', completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (task_row_id,))
        else:
            conn.execute("UPDATE student_tasks SET status = 'todo', completed_at = NULL WHERE id = ?",
                        (task_row_id,))
        conn.commit()
        return StudentProfile.update_stage(user_id)
                        