
from dataclasses import dataclass
from app.models.db import get_db
from app.models.enrollment import current_stage

@dataclass
class StudentProfile:
    user_id: int
    stage: str
    updated_at: str

    @classmethod
    def _from_row(cls, row):
        if row is None:
            return None
        return cls(row["user_id"], row["stage"], row["updated_at"])

    @classmethod
    def get(cls, user_id):
        row = get_db().execute("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()
        return cls._from_row(row)

    @classmethod
    def task_rows(cls, user_id):
        rows = get_db().execute("SELECT * FROM student_tasks where user_id = ?", (user_id,)).fetchall()
        return rows

    @classmethod
    def update_stage(cls, user_id):
        tasks = cls.task_rows(user_id)
        new_stage = current_stage(tasks)
        profile = cls.get(user_id)
        if profile and profile.stage == new_stage:
            return new_stage
        else:
            conn = get_db()
            conn.execute("INSERT INTO student_profiles (user_id, stage) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET stage = excluded.stage, updated_at = CURRENT_TIMESTAMP",
                         (user_id, new_stage))
            conn.execute("INSERT INTO stage_history (user_id, stage) VALUES (?, ?)", (user_id, new_stage))
            conn.commit()
            return new_stage
