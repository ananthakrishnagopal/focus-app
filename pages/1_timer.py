import time
from datetime import datetime

import streamlit as st

from utils.db import init_db, save_session

init_db()

st.set_page_config(page_title="Focus Timer", page_icon="⏱️")
st.title("⏱️ Focus Timer")

# ── session state defaults ────────────────────────────────────────────────────
for key, default in [
    ("timer_running", False),
    ("start_time", None),
    ("elapsed_on_pause", 0),   # accumulated seconds before latest Start
    ("last_task", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── helpers ───────────────────────────────────────────────────────────────────
def elapsed_seconds() -> int:
    if st.session_state.start_time is None:
        return st.session_state.elapsed_on_pause
    delta = datetime.now() - st.session_state.start_time
    return int(delta.total_seconds()) + st.session_state.elapsed_on_pause


def fmt_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ── UI ────────────────────────────────────────────────────────────────────────
task = st.text_input(
    "What are you working on?",
    value=st.session_state.last_task,
    placeholder="e.g. Write project report intro",
)

col1, col2, col3 = st.columns(3)

if col1.button("▶ Start", disabled=st.session_state.timer_running, use_container_width=True):
    if task.strip():
        st.session_state.timer_running = True
        st.session_state.start_time = datetime.now()
        st.session_state.last_task = task
        st.rerun()
    else:
        st.warning("Enter a task before starting.")

if col2.button("⏸ Pause", disabled=not st.session_state.timer_running, use_container_width=True):
    st.session_state.elapsed_on_pause = elapsed_seconds()
    st.session_state.start_time = None
    st.session_state.timer_running = False
    st.rerun()

if col3.button("⏹ Stop & Log", use_container_width=True):
    total = elapsed_seconds()
    st.session_state.timer_running = False
    st.session_state["_pending_log"] = {
        "task_declared": st.session_state.last_task,
        "duration_min": max(1, total // 60),
        "start_time": (
            st.session_state.start_time.isoformat()
            if st.session_state.start_time
            else None
        ),
    }
    # reset timer state
    st.session_state.start_time = None
    st.session_state.elapsed_on_pause = 0
    st.rerun()

# ── live display ──────────────────────────────────────────────────────────────
secs = elapsed_seconds()
st.markdown(
    f"<h1 style='text-align:center;font-size:4rem;letter-spacing:4px'>{fmt_time(secs)}</h1>",
    unsafe_allow_html=True,
)

if st.session_state.timer_running:
    status = st.empty()
    status.info(f"Focusing on: **{st.session_state.last_task}**")
    time.sleep(1)
    st.rerun()

# ── post-session log form ─────────────────────────────────────────────────────
if "_pending_log" in st.session_state and st.session_state["_pending_log"]:
    pending = st.session_state["_pending_log"]
    st.divider()
    st.subheader("Log this session")

    with st.form("log_session"):
        task_actual = st.text_input(
            "What did you actually work on?",
            value=pending["task_declared"],
        )
        finished = st.selectbox("Did you finish?", ["yes", "partial", "no"])
        distractor = st.text_input(
            "Main distractor (leave blank if none)", placeholder="e.g. Slack notifications"
        )
        submitted = st.form_submit_button("Save session")

    if submitted:
        save_session(
            task_declared=pending["task_declared"],
            task_actual=task_actual,
            duration_min=pending["duration_min"],
            finished=finished,
            distractor=distractor.strip() or None,
            start_time=pending.get("start_time"),
        )
        st.session_state["_pending_log"] = None
        st.success(f"Session saved — {pending['duration_min']} min logged.")
        st.balloons()
