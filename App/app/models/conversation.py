from app.models.db import get_db
from datetime import date

class Conversation:
    @classmethod 
    def save_message(cls, user_id, role, content):
        conn=get_db()
        conn.execute("INSERT INTO conversation_messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        conn.commit()
        return content
    
    @classmethod
    def recent_history(cls, user_id, limit=20):
        messages = get_db().execute("SELECT * FROM conversation_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit)).fetchall()
        messages.reverse()
        return messages

    @classmethod
    def daily_message_count(cls, user_id):
        messages = get_db().execute(" SELECT COUNT(*) FROM conversation_messages WHERE user_id = ? AND role = ? AND date(created_at, 'localtime') = ?", (user_id, 'student', date.today().isoformat())).fetchone()[0]
        return messages
    