from __future__ import annotations

from collections import defaultdict
from typing import Any


def completion_rate(sessions: list[dict]) -> float:
    """Fraction of sessions marked 'yes'."""
    if not sessions:
        return 0.0
    done = sum(1 for s in sessions if s.get("finished") == "yes")
    return done / len(sessions)


def task_alignment_rate(sessions: list[dict]) -> float:
    """Fraction where task_actual matches task_declared (case-insensitive strip)."""
    if not sessions:
        return 0.0
    aligned = sum(
        1
        for s in sessions
        if (s.get("task_actual") or "").strip().lower()
        == (s.get("task_declared") or "").strip().lower()
    )
    return aligned / len(sessions)


def total_focused_minutes(sessions: list[dict]) -> int:
    return sum(s.get("duration_min") or 0 for s in sessions)


def sessions_by_day(sessions: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for s in sessions:
        counts[s["date"]] += 1
    return dict(counts)


def top_distractors(sessions: list[dict], n: int = 5) -> list[tuple[str, int]]:
    counts: dict[str, int] = defaultdict(int)
    for s in sessions:
        d = (s.get("distractor") or "").strip()
        if d:
            counts[d] += 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]


def avg_energy(eod_logs: list[dict]) -> float:
    valid = [e["energy"] for e in eod_logs if e.get("energy")]
    return sum(valid) / len(valid) if valid else 0.0


def streak_days(sessions: list[dict]) -> int:
    """Consecutive calendar days (up to today) with at least one session."""
    from datetime import date, timedelta

    days_with_sessions = {s["date"] for s in sessions}
    today = date.today()
    streak = 0
    cursor = today
    while cursor.isoformat() in days_with_sessions:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def finished_counts(sessions: list[dict]) -> dict[str, int]:
    counts = {"yes": 0, "partial": 0, "no": 0}
    for s in sessions:
        key = s.get("finished") or "no"
        if key in counts:
            counts[key] += 1
    return counts
