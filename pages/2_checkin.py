"""Mid-session / between-sessions quick check-in."""
from datetime import date

import streamlit as st

from utils.db import init_db, get_sessions, save_session

init_db()

st.set_page_config(page_title="Check-In", page_icon="✅")
st.title("✅ Quick Check-In")

today = date.today().isoformat()
sessions_today = get_sessions(today, today)

# ── today's summary banner ────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Sessions today", len(sessions_today))
finished_yes = sum(1 for s in sessions_today if s["finished"] == "yes")
col2.metric("Completed", finished_yes)
total_min = sum(s["duration_min"] or 0 for s in sessions_today)
col3.metric("Minutes focused", total_min)

st.divider()

# ── mood / energy pulse ───────────────────────────────────────────────────────
st.subheader("How are you feeling right now?")
energy_now = st.select_slider(
    "Energy level",
    options=[1, 2, 3, 4, 5],
    value=3,
    format_func=lambda x: {1: "😴 Drained", 2: "😕 Low", 3: "😐 OK", 4: "🙂 Good", 5: "🚀 Energised"}[x],
)
if energy_now <= 2:
    st.info("Low energy detected — consider a 5-min break or a water/snack.")

st.divider()

# ── log a quick note or mini-session ─────────────────────────────────────────
st.subheader("Log a quick session")

with st.form("quick_log"):
    task_d = st.text_input("Task you just did", placeholder="e.g. Reviewed PR #42")
    task_a = st.text_input("What actually happened?", placeholder="Same as above, or drift...")
    col_a, col_b = st.columns(2)
    dur = col_a.number_input("Duration (min)", min_value=1, max_value=240, value=25)
    done = col_b.selectbox("Finished?", ["yes", "partial", "no"])
    distractor = st.text_input("Distractor (optional)")
    save = st.form_submit_button("Save")

if save:
    if task_d.strip():
        save_session(
            task_declared=task_d.strip(),
            task_actual=task_a.strip() or task_d.strip(),
            duration_min=int(dur),
            finished=done,
            distractor=distractor.strip() or None,
        )
        st.success("Session logged!")
        st.rerun()
    else:
        st.warning("Task name is required.")

st.divider()

# ── today's session list ──────────────────────────────────────────────────────
if sessions_today:
    st.subheader("Today's sessions")
    for s in reversed(sessions_today):
        icon = {"yes": "✅", "partial": "🔶", "no": "❌"}.get(s["finished"], "")
        with st.expander(f"{icon} {s['task_declared']} — {s['duration_min']} min"):
            if s["task_actual"] and s["task_actual"] != s["task_declared"]:
                st.write(f"**Actual:** {s['task_actual']}")
            if s["distractor"]:
                st.write(f"**Distractor:** {s['distractor']}")
else:
    st.info("No sessions logged yet today. Start your first one in the Timer page!")
