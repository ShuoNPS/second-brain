import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "second_brain.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                url TEXT,
                title TEXT,
                duration_seconds INTEGER,
                raw_data TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                sender TEXT,
                subject TEXT,
                snippet TEXT,
                category TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


def insert_activity(source: str, category: str, timestamp: str,
                    url: str, title: str, duration_seconds: int, raw_data: str):
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO activities
            (source, category, timestamp, url, title, duration_seconds, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (source, category, timestamp, url, title, duration_seconds, raw_data))
        conn.commit()


def insert_email(message_id: str, timestamp: str, sender: str,
                 subject: str, snippet: str, category: str):
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO emails
            (message_id, timestamp, sender, subject, snippet, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (message_id, timestamp, sender, subject, snippet, category))
        conn.commit()


def get_activities_today() -> list[dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM activities
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (today,)).fetchall()
    return [dict(r) for r in rows]


def get_emails_today() -> list[dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM emails
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (today,)).fetchall()
    return [dict(r) for r in rows]
