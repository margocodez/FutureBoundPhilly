from app.models.db import get_db
import smtplib
from collections import defaultdict
from email.message import EmailMessage
from datetime import date
from flask import current_app, url_for

class Reminder:
    @classmethod
    def due_soon(cls, days):
        excluded_emails = set(current_app.config["STAFF_EMAILS"]) | set(current_app.config["MENTOR_EMAILS"])

        placeholders = ",".join("?" for _ in excluded_emails)
        exclusion_sql = (
            f"AND LOWER(u.email) NOT IN ({placeholders})"
            if excluded_emails
            else ""
        )

        sql = f"""
            SELECT
                u.name AS student_name,
                u.email AS student_email,
                c.user_id AS user_id,
                c.title AS task_title,
                c.due_date AS due_date,
                c.id AS task_row_id
            FROM student_tasks AS c
            JOIN users AS u ON u.id = c.user_id
            WHERE c.status != 'done'
              AND c.due_date IS NOT NULL
              AND date(c.due_date) BETWEEN
                  date('now', 'localtime')
                  AND date('now', 'localtime', ?)
              AND NOT EXISTS (
                  SELECT 1
                  FROM reminders_sent AS r
                  WHERE r.task_row_id = c.id
              )
              {exclusion_sql}
            ORDER BY u.email, date(c.due_date), c.title
        """

        params = (
            ["+" + str(days) + " days"]
            + sorted(email.lower() for email in excluded_emails)
        )

        return get_db().execute(sql, params).fetchall()

    @classmethod
    def send_all(cls, days):
        rows = cls.due_soon(days)
        students = defaultdict(list)

        for row in rows:
            email = row["student_email"]
            students[email].append(row)

        sent_count = 0

        for email, tasks in students.items():
            name = tasks[0]["student_name"] or ""
            first_name=name.split()[0] if name.strip() else "there"
            task_lines = [
                f"- {task['task_title']} (due {date.fromisoformat(task['due_date']).strftime('%b %d, %Y')})"
                for task in tasks
            ]

            checklist_url = url_for("interview.checklist", _external=True)

            subject = "Upcoming enrollment tasks"
            body = (
                f"Hi {first_name},\n\n"
                "Here are your upcoming enrollment tasks:\n\n"
                + "\n".join(task_lines)
                + "\n\nLog in to FutureBound Philly to review your checklist "
                  "and mark tasks complete when finished.\n"
                + f"\nOpen your checklist: {checklist_url}\n"
            )

            if not cls._send_email(email, subject, body):
                continue

            for task in tasks:
                get_db().execute(
                    """
                    INSERT OR IGNORE INTO reminders_sent (user_id, task_row_id)
                    VALUES (?, ?)
                    """,
                    (task["user_id"], task["task_row_id"],),
                )

            get_db().commit()
            sent_count += 1

        return sent_count

    @classmethod
    def _send_email(cls, to, subject, body):
        username = current_app.config.get("MAIL_USERNAME")
        mail_password = current_app.config.get(
            "MAIL_PASSWORD"
        )
        if not username or not mail_password:
            print(
                "\n--- EMAIL PREVIEW ---\n"
                f"To: {to}\n"
                f"Subject: {subject}\n\n"
                f"{body}\n"
                "--- END EMAIL ---\n"
            )
            return True
        try:
            message = EmailMessage()
            message["From"] = username
            message["To"] = to
            message["Subject"] = subject
            message.set_content(body)

            mail_server = current_app.config.get(
                "MAIL_SERVER"
            )
            mail_port = int(
                current_app.config.get("MAIL_PORT")
            )
            use_tls = current_app.config.get("MAIL_USE_TLS", True)

            with smtplib.SMTP(mail_server, mail_port, timeout=15) as server:
                if use_tls:
                    server.starttls()

                if mail_password:
                    server.login(username, mail_password)

                server.send_message(message)
        except (smtplib.SMTPException, OSError) as e:
            print("Email failed:", e, flush=True)
            return False
        return True