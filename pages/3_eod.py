from datetime import date

import streamlit as st

from utils.db import init_db, get_sessions, save_eod, get_eod_logs
from utils.style import apply_style, render_topnav, status_badge

init_db()

st.set_page_config(page_title="End of day", page_icon=None)
apply_style()
render_topnav()

st.title("End of day")

today = date.today().isoformat()
sessions_today = get_sessions(today, today)
existing_eod = get_eod_logs(today, today)

# ── today at a glance ─────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Sessions", len(sessions_today))
done_count = sum(1 for s in sessions_today if s["finished"] == "yes")
col2.metric("Done", done_count)
total_min = sum(s["duration_min"] or 0 for s in sessions_today)
col3.metric("Focus min", total_min)

if sessions_today:
    with st.expander("Session log"):
        for s in sessions_today:
            badge = status_badge(s["finished"])
            drift = f" — drift: {s['task_actual']}" if s["task_actual"] != s["task_declared"] else ""
            st.markdown(
                f"{badge}&nbsp; **{s['task_declared']}** · {s['duration_min']} min{drift}",
                unsafe_allow_html=True,
            )

st.divider()

# ── reflection form ───────────────────────────────────────────────────────────
st.subheader("Reflection")

prefill = existing_eod[0] if existing_eod else {}

with st.form("eod_form"):
    energy = st.select_slider(
        "Overall energy",
        options=[1, 2, 3, 4, 5],
        value=int(prefill.get("energy", 3)),
        format_func=lambda x: {
            1: "1 — Exhausted",
            2: "2 — Low",
            3: "3 — OK",
            4: "4 — Good",
            5: "5 — Great",
        }[x],
    )
    sessions_done_input = st.number_input(
        "Sessions completed",
        min_value=0,
        value=int(prefill.get("sessions_done", done_count)),
    )
    biggest_win = st.text_area(
        "Biggest win",
        value=prefill.get("biggest_win", ""),
        placeholder="Shipped a fix, held a clear 25-min block...",
    )
    biggest_hijack = st.text_area(
        "Biggest hijack",
        value=prefill.get("biggest_hijack", ""),
        placeholder="What derailed your focus the most?",
    )
    notes = st.text_area(
        "Notes (optional)",
        value=prefill.get("notes", ""),
        placeholder="Mood, blockers, plans for tomorrow...",
    )
    label = "Update" if existing_eod else "Save"
    submitted = st.form_submit_button(label)

if submitted:
    if biggest_win.strip() and biggest_hijack.strip():
        save_eod(
            energy=int(energy),
            sessions_done=int(sessions_done_input),
            biggest_win=biggest_win.strip(),
            biggest_hijack=biggest_hijack.strip(),
            notes=notes.strip(),
        )
        st.success("Reflection saved.")
    else:
        st.warning("Fill in both biggest win and biggest hijack.")
