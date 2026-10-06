import hashlib
import secrets
from dataclasses import dataclass

from app.models.db import get_db


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


@dataclass
class User:
    id: int
    google_sub: str
    email: str
    name: str
    has_token: bool

    @classmethod
    def _from_row(cls, row):
        if row is None:
            return None
        return cls(row["id"], row["google_sub"], row["email"], row["name"],
                   row["api_token_hash"] is not None)

    @classmethod
    def get(cls, user_id):
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return cls._from_row(row)

    @classmethod
    def upsert_from_google(cls, userinfo):
        """Create the user on first sign-in; refresh email/name on later ones."""
        conn = get_db()
        conn.execute(
            """INSERT INTO users (google_sub, email, name) VALUES (?, ?, ?)
               ON CONFLICT(google_sub) DO UPDATE SET email = excluded.email, name = excluded.name""",
            (userinfo["sub"], userinfo["email"], userinfo.get("name")),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE google_sub = ?", (userinfo["sub"],)).fetchone()
        return cls._from_row(row)

    @classmethod
    def from_api_token(cls, token):
        row = get_db().execute(
            "SELECT * FROM users WHERE api_token_hash = ?", (_hash(token),)
        ).fetchone()
        return cls._from_row(row)

    def regenerate_api_token(self):
        """Issue a new token (invalidating the old one). Only the hash is stored."""
        token = secrets.token_urlsafe(32)
        conn = get_db()
        conn.execute("UPDATE users SET api_token_hash = ? WHERE id = ?", (_hash(token), self.id))
        conn.commit()
        self.has_token = True
        return token
