from app.models.db import get_db

class Mentor:
    @classmethod
    def open_request(cls, user_id):
        return get_db().execute("SELECT * FROM mentor_requests WHERE user_id = ? AND status = 'open'", (user_id,)).fetchone()

    @classmethod
    def create_request(cls, user_id, help_with, best_time):
        conn = get_db()
        conn.execute("INSERT INTO mentor_requests (user_id, help_with, best_time) VALUES (?, ?, ?)", (user_id, help_with, best_time))
        conn.commit()

    @classmethod
    def assign(cls, user_id, mentor_email):
        conn = get_db()
        conn.execute("INSERT OR REPLACE INTO mentor_assignments (user_id, mentor_email) VALUES (?, ?)", (user_id, mentor_email))
        conn.execute("UPDATE mentor_requests SET status = 'assigned' WHERE user_id = ? AND status = 'open'", (user_id,))
        conn.commit()

    @classmethod
    def assignment_for(cls, user_id):
        return get_db().execute("SELECT m.mentor_email, m.assigned_at, COALESCE(u.name, m.mentor_email) AS mentor_name FROM mentor_assignments m LEFT JOIN users u ON lower(u.email) = m.mentor_email WHERE m.user_id = ?", (user_id,)).fetchone()

    @classmethod
    def students_for(cls, mentor_email):
        return get_db().execute("""SELECT u.id, u.name, u.email, m.assigned_at, r.help_with, r.best_time
                                    FROM mentor_assignments m
                                    JOIN users u ON u.id = m.user_id
                                    LEFT JOIN mentor_requests r
                                    ON r.id = (SELECT MAX(id) FROM mentor_requests WHERE user_id = m.user_id)
                                    WHERE m.mentor_email = ?
                                    ORDER BY m.assigned_at DESC""", (mentor_email,)).fetchall()
    
