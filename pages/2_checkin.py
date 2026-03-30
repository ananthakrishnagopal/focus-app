from datetime import date

import streamlit as st

from utils.db import init_db, get_sessions, save_session, delete_session
from utils.style import apply_style, status_badge

init_db()

st.set_page_config(page_title="Check-in", page_icon=None)
apply_style()

st.title("Check-in")

today = date.today().isoformat()
sessions_today = get_sessions(today, today)

# ── today's summary ───────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Sessions", len(sessions_today))
finished_yes = sum(1 for s in sessions_today if s["finished"] == "yes")
col2.metric("Done", finished_yes)
total_min = sum(s["duration_min"] or 0 for s in sessions_today)
col3.metric("Focus min", total_min)

st.divider()

# ── energy pulse ──────────────────────────────────────────────────────────────
st.subheader("Energy right now")
energy_now = st.select_slider(
    "Level",
    options=[1, 2, 3, 4, 5],
    value=3,
    format_func=lambda x: {
        1: "1 — Drained",
        2: "2 — Low",
        3: "3 — OK",
        4: "4 — Good",
        5: "5 — Energised",
    }[x],
    label_visibility="collapsed",
)
if energy_now <= 2:
    st.info("Low energy — consider a short break.")

st.divider()

# ── quick log ─────────────────────────────────────────────────────────────────
st.subheader("Log a session")

with st.form("quick_log"):
    task_d = st.text_input("Task", placeholder="e.g. Reviewed PR #42")
    task_a = st.text_input("What actually happened?", placeholder="Same, or describe drift")
    col_a, col_b = st.columns(2)
    dur = col_a.number_input("Duration (min)", min_value=1, max_value=240, value=25)
    done = col_b.selectbox("Finished?", ["yes", "partial", "no"])
    distractor = st.text_input("Distractor", placeholder="Optional")
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
        st.success("Saved.")
        st.rerun()
    else:
        st.warning("Task name is required.")

st.divider()

# ── today's session list ──────────────────────────────────────────────────────
if sessions_today:
    st.subheader("Today")
    for s in reversed(sessions_today):
        badge = status_badge(s["finished"])
        with st.expander(f"{s['task_declared']}  ·  {s['duration_min']} min"):
            st.markdown(badge, unsafe_allow_html=True)
            if s["task_actual"] and s["task_actual"] != s["task_declared"]:
                st.markdown(f"**Actual:** {s['task_actual']}")
            if s["distractor"]:
                st.markdown(f"**Distractor:** {s['distractor']}")
            if st.button("Delete", key=f"del_{s['id']}"):
                delete_session(s["id"])
                st.rerun()
else:
    st.caption("No sessions logged yet. Use the Timer page to start one.")
