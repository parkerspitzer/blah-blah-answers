import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_DIR.mkdir(exist_ok=True)
DB_PATH = _DATA_DIR / "conversations.db"

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


def expire_history_if_stale(phone, timeout_minutes):
    """Clear history if the last message is older than timeout_minutes.

    Returns True if history was expired, False otherwise.
    """
    conn = _get_conn()
    row = conn.execute(
        "SELECT created_at FROM messages WHERE phone = ? ORDER BY id DESC LIMIT 1",
        (phone,),
    ).fetchone()
    if not row:
        return False
    last_ts = datetime.fromisoformat(row[0]).replace(tzinfo=timezone.utc)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
    if last_ts < cutoff:
        clear_history(phone)
        return True
    return False


def get_last_user_message(phone):
    """Return the content of the most recent user message, or None."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT content FROM messages WHERE phone = ? AND role = 'user' ORDER BY id DESC LIMIT 1",
        (phone,),
    ).fetchone()
    return row[0] if row else None
