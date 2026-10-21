from app.models.db import get_db

class Staff:
    @classmethod
    def priority_list(cls):
        risks = get_db().execute("SELECT u.id, u.name, u.email, i.risk_score, i.risk_category, i.completed_at, p.stage, (SELECT COUNT(*) FROM student_tasks t WHERE t.user_id = u.id AND t.status != 'done' AND t.due_date < date('now', 'localtime')) AS overdue FROM users u LEFT JOIN interviews i ON i.user_id = u.id AND i.id = (SELECT MAX(id) FROM interviews WHERE user_id = u.id) LEFT JOIN student_profiles p ON p.user_id = u.id ORDER BY i.risk_score DESC, overdue DESC").fetchall()
        return risks