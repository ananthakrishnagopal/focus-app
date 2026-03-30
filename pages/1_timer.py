import time
from datetime import datetime

import streamlit as st

from utils.db import init_db, save_session
from utils.style import apply_style, render_topnav

init_db()

st.set_page_config(page_title="Timer", page_icon=None)
apply_style()
render_topnav()

st.title("Timer")

# ── session state defaults ────────────────────────────────────────────────────
for key, default in [
    ("timer_running", False),
    ("start_time", None),
    ("elapsed_on_pause", 0),
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


# ── task input ────────────────────────────────────────────────────────────────
task = st.text_input(
    "What are you working on?",
    value=st.session_state.last_task,
    placeholder="e.g. Write project report intro",
)

# ── controls ──────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

if col1.button("Start", disabled=st.session_state.timer_running, use_container_width=True):
    if task.strip():
        st.session_state.timer_running = True
        st.session_state.start_time = datetime.now()
        st.session_state.last_task = task
        st.rerun()
    else:
        st.warning("Enter a task before starting.")

if col2.button("Pause", disabled=not st.session_state.timer_running, use_container_width=True):
    st.session_state.elapsed_on_pause = elapsed_seconds()
    st.session_state.start_time = None
    st.session_state.timer_running = False
    st.rerun()

if col3.button("Stop + log", use_container_width=True):
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
    st.session_state.start_time = None
    st.session_state.elapsed_on_pause = 0
    st.rerun()

# ── clock display ─────────────────────────────────────────────────────────────
secs = elapsed_seconds()
st.markdown(
    f"""
    <div style='text-align:center;padding:2.5rem 0 1.5rem'>
        <span style='font-size:4.5rem;font-weight:300;letter-spacing:-0.02em;
                     font-family:"SF Mono","Fira Mono","Courier New",monospace;
                     color:#111'>{fmt_time(secs)}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.timer_running:
    st.markdown(
        f"<p style='text-align:center;color:#888;font-size:0.85rem'>"
        f"{st.session_state.last_task}</p>",
        unsafe_allow_html=True,
    )
    time.sleep(1)
    st.rerun()

# ── post-session log form ─────────────────────────────────────────────────────
if st.session_state.get("_pending_log"):
    pending = st.session_state["_pending_log"]
    st.divider()
    st.subheader("Log a session")

    with st.form("log_session"):
        task_actual = st.text_input(
            "What actually happened?",
            value=pending["task_declared"],
        )
        finished = st.selectbox("Finished?", ["yes", "partial", "no"])
        distractor = st.text_input(
            "Distractor", placeholder="Optional"
        )
        submitted = st.form_submit_button("Save")

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
        st.success(f"Saved — {pending['duration_min']} min logged.")
