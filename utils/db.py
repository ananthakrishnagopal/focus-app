import sqlite3
from pathlib import Path
from datetime import date, datetime
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "focus.db"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                date          TEXT    NOT NULL,
                task_declared TEXT    NOT NULL,
                task_actual   TEXT,
                duration_min  INTEGER,
                finished      TEXT    CHECK(finished IN ('yes', 'partial', 'no')),
                distractor    TEXT,
                start_time    TEXT
            );

            CREATE TABLE IF NOT EXISTS eod_logs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                date          TEXT    NOT NULL UNIQUE,
                energy        INTEGER CHECK(energy BETWEEN 1 AND 5),
                sessions_done INTEGER,
                biggest_win   TEXT,
                biggest_hijack TEXT,
                notes         TEXT
            );
        """)


def save_session(
    task_declared: str,
    task_actual: str,
    duration_min: int,
    finished: str,
    distractor: Optional[str] = None,
    start_time: Optional[str] = None,
    session_date: Optional[str] = None,
) -> int:
    d = session_date or date.today().isoformat()
    with _conn() as conn:
        cur = conn.execute(
            """INSERT INTO sessions
               (date, task_declared, task_actual, duration_min, finished, distractor, start_time)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (d, task_declared, task_actual, duration_min, finished, distractor, start_time),
        )
        return cur.lastrowid


def save_eod(
    energy: int,
    sessions_done: int,
    biggest_win: str,
    biggest_hijack: str,
    notes: str = "",
    log_date: Optional[str] = None,
) -> None:
    d = log_date or date.today().isoformat()
    with _conn() as conn:
        conn.execute(
            """INSERT INTO eod_logs
               (date, energy, sessions_done, biggest_win, biggest_hijack, notes)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(date) DO UPDATE SET
                   energy        = excluded.energy,
                   sessions_done = excluded.sessions_done,
                   biggest_win   = excluded.biggest_win,
                   biggest_hijack = excluded.biggest_hijack,
                   notes         = excluded.notes""",
            (d, energy, sessions_done, biggest_win, biggest_hijack, notes),
        )


def get_sessions(start: str, end: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM sessions WHERE date BETWEEN ? AND ? ORDER BY date, id",
            (start, end),
        ).fetchall()
    return [dict(r) for r in rows]


def get_eod_logs(start: str, end: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM eod_logs WHERE date BETWEEN ? AND ? ORDER BY date",
            (start, end),
        ).fetchall()
    return [dict(r) for r in rows]


def count_sessions_today() -> int:
    today = date.today().isoformat()
    with _conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE date = ?", (today,)
        ).fetchone()
    return row[0]
