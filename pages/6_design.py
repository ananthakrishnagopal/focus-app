import streamlit as st
from utils.style import apply_style, render_topnav

st.set_page_config(page_title="Design & Architecture", page_icon=None)
apply_style()
render_topnav()

st.title("Design & Architecture")
st.caption("How the app is built and why decisions were made.")

st.divider()

# ── stack ─────────────────────────────────────────────────────────────────────
st.subheader("Stack")
st.markdown("""
| Layer | Choice | Why |
|---|---|---|
| UI | Streamlit | Fast to build, no JS required, Python-native |
| Database | SQLite (via stdlib `sqlite3`) | Local-first, zero config, no server |
| Analytics | Pure Python (`utils/analytics.py`) | No pandas dependency for logic, only for display |
| Charts | Streamlit native (`st.bar_chart`, `st.line_chart`) | Sufficient for the use case, no extra deps |
| Styling | Injected CSS via `st.markdown` | Streamlit's theming API is limited; CSS gives full control |
""")

st.divider()

# ── file structure ────────────────────────────────────────────────────────────
st.subheader("File structure")
st.code("""
focus-app/
├── app.py                  # Home page — context-aware nudge
├── focus.db                # SQLite database (auto-created)
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Theme: warm off-white, near-black text
├── pages/
│   ├── 1_timer.py          # Focus session timer
│   ├── 2_checkin.py        # Mid-day check-in + session log
│   ├── 3_eod.py            # End-of-day reflection
│   ├── 4_dashboard.py      # Analytics dashboard
│   ├── 5_docs.py           # This docs page
│   └── 6_design.py         # This page
└── utils/
    ├── __init__.py
    ├── db.py               # All database access
    ├── analytics.py        # Pure-Python analytics functions
    └── style.py            # CSS injection + shared UI helpers
""", language="text")

st.divider()

# ── database schema ───────────────────────────────────────────────────────────
st.subheader("Database schema")

with st.expander("sessions"):
    st.code("""
CREATE TABLE sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    date          TEXT    NOT NULL,          -- ISO date: 2026-03-30
    task_declared TEXT    NOT NULL,          -- what you said you'd do
    task_actual   TEXT,                      -- what you actually did
    duration_min  INTEGER,                   -- session length in minutes
    finished      TEXT CHECK(finished IN ('yes', 'partial', 'no')),
    distractor    TEXT,                      -- nullable, free text
    start_time    TEXT                       -- ISO datetime, nullable
);
""", language="sql")

with st.expander("eod_logs"):
    st.code("""
CREATE TABLE eod_logs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    date           TEXT    NOT NULL UNIQUE,  -- one row per day
    energy         INTEGER CHECK(energy BETWEEN 1 AND 5),
    sessions_done  INTEGER,
    biggest_win    TEXT,
    biggest_hijack TEXT,
    notes          TEXT
);
""", language="sql")

st.divider()

# ── analytics ─────────────────────────────────────────────────────────────────
st.subheader("Analytics functions")
st.markdown("""
All defined in `utils/analytics.py`. No side effects — each function takes a list of session dicts and returns a value.

| Function | Returns |
|---|---|
| `completion_rate(sessions)` | Float 0–1: fraction of sessions marked `yes` |
| `task_alignment_rate(sessions)` | Float 0–1: fraction where declared == actual (case-insensitive) |
| `total_focused_minutes(sessions)` | Integer: sum of `duration_min` |
| `sessions_by_day(sessions)` | Dict of date → count |
| `top_distractors(sessions, n)` | List of (distractor, count) tuples, sorted descending |
| `avg_energy(eod_logs)` | Float: mean energy across EOD logs |
| `streak_days(sessions)` | Integer: consecutive days back from today with ≥1 session |
| `finished_counts(sessions)` | Dict with keys `yes`, `partial`, `no` |
""")

st.divider()

# ── design decisions ──────────────────────────────────────────────────────────
st.subheader("Design decisions")

with st.expander("Timer: no background threads"):
    st.markdown("""
Streamlit rerenders the entire script on each interaction. Rather than using `threading` or `asyncio` to tick a clock, the timer stores `start_time` in `st.session_state` and computes `elapsed = now - start_time` on every render. A `time.sleep(1)` + `st.rerun()` loop drives the live update while the timer is running. This is idiomatic Streamlit and avoids state synchronisation bugs.
""")

with st.expander("EOD upsert on date"):
    st.markdown("""
`eod_logs` has a `UNIQUE` constraint on `date`. The `save_eod()` function uses `INSERT ... ON CONFLICT(date) DO UPDATE`, so submitting the EOD form a second time on the same day updates rather than duplicates the record. No separate edit flow needed.
""")

with st.expander("Styling via injected CSS"):
    st.markdown("""
Streamlit's `config.toml` theming sets broad colours and font. Fine-grained control (button hover states, metric card padding, transparent header, fixed nav) requires injecting a `<style>` block via `st.markdown(..., unsafe_allow_html=True)`. This is centralised in `utils/style.py` so all pages share the same rules without duplication.
""")

with st.expander("Context-aware home page"):
    st.markdown("""
The home page reads time of day + today's session/EOD state to surface one primary action. The four states are:

| Condition | Heading | CTA |
|---|---|---|
| 0 sessions today | Ready to focus? | Start a session |
| Sessions exist, before 5pm | Keep going. | Start another session |
| After 5pm, no EOD | Good work today. | Log end of day |
| After 5pm, EOD done | Day logged. | View dashboard |

This removes the "what should I do now?" decision — the main friction point for ADHD.
""")

with st.expander("No external auth or sync"):
    st.markdown("""
The app is intentionally local-only. Adding accounts, sync, or a remote database would introduce friction (login, connectivity dependency) and complexity that isn't justified for a personal focus tool. The SQLite file is fully portable and can be backed up with a single file copy.
""")
