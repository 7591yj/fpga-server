import sqlite3
import time
from pathlib import Path

DB_PATH = Path("/opt/fpga_app/config/jobs.db")


def _db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_sessions_table():
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                id INTEGER,
                ts REAL
            )
        """)


def save_session(token, username, id):
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sessions (token, username, id, ts) VALUES (?, ?, ?, ?)",
            (token, username, id, time.time()),
        )


def get_session(token):
    with _db() as conn:
        row = conn.execute(
            "SELECT username, id, ts FROM sessions WHERE token=?", (token,)
        ).fetchone()
    if not row:
        return None
    return {"user": row[0], "id": row[1], "ts": row[2]}


def delete_session(token):
    with _db() as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
