from datetime import date

import streamlit as st

from utils.db import init_db, get_sessions
from utils.style import apply_style

init_db()

st.set_page_config(
    page_title="Focus",
    page_icon=None,
    layout="centered",
)
apply_style()

st.title("Focus")
st.caption("One task at a time.")

st.divider()

today = date.today().isoformat()
sessions_today = get_sessions(today, today)
done_today = sum(1 for s in sessions_today if s["finished"] == "yes")
min_today = sum(s["duration_min"] or 0 for s in sessions_today)

col1, col2, col3 = st.columns(3)
col1.metric("Sessions", len(sessions_today))
col2.metric("Done", done_today)
col3.metric("Focus min", min_today)

st.divider()

st.markdown("""
### Pages

| | |
|---|---|
| **Timer** | Start a session, track time, log when done |
| **Check-in** | Mid-day pulse — quick log, today's progress |
| **End of day** | Reflection: energy, wins, what hijacked you |
| **Dashboard** | Analytics across 7 / 14 / 30 / 90 days |

Navigate using the sidebar.
""")

if not sessions_today:
    st.info("No sessions yet today — open the Timer page to start.")
