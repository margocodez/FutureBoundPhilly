from app.models.db import get_db

class Staff:
    @classmethod
    def priority_list(cls):
        risks = get_db().execute("SELECT u.id, u.name, u.email, i.risk_score, i.risk_category, i.completed_at, p.stage, m.mentor_email, COALESCE(mu.name, m.mentor_email) AS mentor_name, (SELECT COUNT(*) FROM student_tasks t WHERE t.user_id = u.id AND t.status != 'done' AND t.due_date < date('now', 'localtime')) AS overdue FROM users u LEFT JOIN interviews i ON i.user_id = u.id AND i.id = (SELECT MAX(id) FROM interviews WHERE user_id = u.id) LEFT JOIN student_profiles p ON p.user_id = u.id LEFT JOIN mentor_assignments m ON m.user_id = u.id LEFT JOIN users mu ON lower(mu.email) = m.mentor_email ORDER BY i.risk_score DESC, overdue DESC").fetchall()
        return risks