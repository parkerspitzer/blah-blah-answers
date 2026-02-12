import json
import sqlite3
import threading
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "conversations.db"

_local = threading.local()


def _get_conn():
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(str(DB_PATH))
        _local.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _local.conn.commit()
    return _local.conn


def add_message(phone, role, content):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO messages (phone, role, content) VALUES (?, ?, ?)",
        (phone, role, content),
    )
    conn.commit()


def get_history(phone, limit):
    if limit <= 0:
        return []
    conn = _get_conn()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE phone = ? ORDER BY id DESC LIMIT ?",
        (phone, limit),
    ).fetchall()
    # Rows come back newest-first, reverse to chronological order
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def clear_history(phone):
    conn = _get_conn()
    conn.execute("DELETE FROM messages WHERE phone = ?", (phone,))
    conn.commit()
