"""End-of-day reflection log."""
from datetime import date

import streamlit as st

from utils.db import init_db, get_sessions, save_eod, get_eod_logs, count_sessions_today

init_db()

st.set_page_config(page_title="EOD Reflection", page_icon="🌙")
st.title("🌙 End-of-Day Reflection")

today = date.today().isoformat()
sessions_today = get_sessions(today, today)
existing_eod = get_eod_logs(today, today)

# ── today's stats as context ──────────────────────────────────────────────────
st.subheader("Today at a glance")
col1, col2, col3 = st.columns(3)
col1.metric("Sessions", len(sessions_today))
done_count = sum(1 for s in sessions_today if s["finished"] == "yes")
col2.metric("Completed", done_count)
total_min = sum(s["duration_min"] or 0 for s in sessions_today)
col3.metric("Total focus (min)", total_min)

if sessions_today:
    with st.expander("See all sessions"):
        for s in sessions_today:
            icon = {"yes": "✅", "partial": "🔶", "no": "❌"}.get(s["finished"], "")
            st.markdown(f"- {icon} **{s['task_declared']}** — {s['duration_min']} min"
                        + (f" _(drift: {s['task_actual']})_" if s["task_actual"] != s["task_declared"] else ""))

st.divider()

# ── reflection form ───────────────────────────────────────────────────────────
st.subheader("Reflection")

prefill = existing_eod[0] if existing_eod else {}

with st.form("eod_form"):
    energy = st.select_slider(
        "Overall energy today",
        options=[1, 2, 3, 4, 5],
        value=int(prefill.get("energy", 3)),
        format_func=lambda x: {1: "1 — Exhausted", 2: "2 — Low", 3: "3 — OK", 4: "4 — Good", 5: "5 — Great"}[x],
    )
    sessions_done_input = st.number_input(
        "Sessions completed (auto-filled, adjust if needed)",
        min_value=0,
        value=int(prefill.get("sessions_done", done_count)),
    )
    biggest_win = st.text_area(
        "Biggest win today",
        value=prefill.get("biggest_win", ""),
        placeholder="Even small wins count — shipped a fix, had a clear 25-min block...",
    )
    biggest_hijack = st.text_area(
        "Biggest focus hijack",
        value=prefill.get("biggest_hijack", ""),
        placeholder="What derailed you the most?",
    )
    notes = st.text_area(
        "Anything else (optional)",
        value=prefill.get("notes", ""),
        placeholder="Mood, blockers, plans for tomorrow...",
    )
    submitted = st.form_submit_button("Save reflection" if not existing_eod else "Update reflection")

if submitted:
    if biggest_win.strip() and biggest_hijack.strip():
        save_eod(
            energy=int(energy),
            sessions_done=int(sessions_done_input),
            biggest_win=biggest_win.strip(),
            biggest_hijack=biggest_hijack.strip(),
            notes=notes.strip(),
        )
        st.success("Reflection saved! Great job today. 🌟")
        st.balloons()
    else:
        st.warning("Please fill in both 'biggest win' and 'biggest hijack'.")
