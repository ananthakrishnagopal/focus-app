"""ADHD Focus Tracker — main entry point."""
from datetime import date

import streamlit as st

from utils.db import init_db, get_sessions, count_sessions_today

init_db()

st.set_page_config(
    page_title="ADHD Focus Tracker",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 ADHD Focus Tracker")
st.caption("Small wins. One task at a time.")

st.divider()

today = date.today().isoformat()
sessions_today = get_sessions(today, today)
done_today = sum(1 for s in sessions_today if s["finished"] == "yes")
min_today = sum(s["duration_min"] or 0 for s in sessions_today)

col1, col2, col3 = st.columns(3)
col1.metric("Sessions today", len(sessions_today))
col2.metric("Completed", done_today)
col3.metric("Focus minutes", min_today)

st.divider()

st.markdown("""
### Navigation

| Page | What it does |
|------|-------------|
| **⏱️ Timer** | Start a focus session, track elapsed time, and log it when done |
| **✅ Check-In** | Quick mid-day pulse — log a session or see today's progress |
| **🌙 EOD** | End-of-day reflection: energy, biggest win, biggest hijack |
| **📊 Dashboard** | Analytics over the last 7 / 14 / 30 / 90 days |

Use the **sidebar** to navigate between pages.
""")

if not sessions_today:
    st.info("No sessions yet today — head to the **Timer** page to start your first focus block!")
