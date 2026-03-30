from datetime import date, datetime

import streamlit as st

from utils.db import init_db, get_sessions, get_eod_logs
from utils.style import apply_style

init_db()

st.set_page_config(page_title="Focus", page_icon=None, layout="centered")
apply_style()

# ── state ─────────────────────────────────────────────────────────────────────
today = date.today().isoformat()
now_hour = datetime.now().hour

sessions_today = get_sessions(today, today)
eod_today = get_eod_logs(today, today)

n_sessions   = len(sessions_today)
n_done       = sum(1 for s in sessions_today if s["finished"] == "yes")
min_today    = sum(s["duration_min"] or 0 for s in sessions_today)
eod_logged   = bool(eod_today)
evening      = now_hour >= 17   # 5 pm+

# ── context-aware nudge ───────────────────────────────────────────────────────
if n_sessions == 0:
    heading = "Ready to focus?"
    subtext = "No sessions yet today. Start with one task — just one."
    cta_label = "Start a session"
    cta_page  = "pages/1_timer.py"

elif evening and not eod_logged:
    heading = "Good work today."
    subtext  = f"{n_sessions} session{'s' if n_sessions != 1 else ''} · {min_today} min focused. Take a moment to reflect."
    cta_label = "Log end of day"
    cta_page  = "pages/3_eod.py"

elif evening and eod_logged:
    heading = "Day logged."
    subtext  = f"{n_sessions} session{'s' if n_sessions != 1 else ''} · {min_today} min · {n_done} done. See you tomorrow."
    cta_label = "View dashboard"
    cta_page  = "pages/4_dashboard.py"

else:
    heading = "Keep going."
    subtext  = f"{n_sessions} session{'s' if n_sessions != 1 else ''} done · {min_today} min focused so far."
    cta_label = "Start another session"
    cta_page  = "pages/1_timer.py"

# ── hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style='padding: 3rem 0 2rem'>
        <p style='font-size:0.75rem;letter-spacing:0.1em;text-transform:uppercase;
                  color:#999;margin-bottom:0.4rem'>
            {date.today().strftime('%A, %B %-d')}
        </p>
        <h1 style='font-size:2.2rem;font-weight:500;letter-spacing:-0.03em;
                   color:#111;margin:0 0 0.6rem'>{heading}</h1>
        <p style='color:#888;font-size:0.95rem;margin:0'>{subtext}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.page_link(cta_page, label=cta_label)

# ── secondary links ───────────────────────────────────────────────────────────
st.markdown(
    "<p style='font-size:0.75rem;color:#bbb;margin:2rem 0 0.5rem;"
    "letter-spacing:0.06em;text-transform:uppercase'>Other pages</p>",
    unsafe_allow_html=True,
)

other_pages = [
    ("pages/1_timer.py",      "Timer"),
    ("pages/2_checkin.py",    "Check-in"),
    ("pages/3_eod.py",        "End of day"),
    ("pages/4_dashboard.py",  "Dashboard"),
]
cols = st.columns(len(other_pages))
for col, (path, label) in zip(cols, other_pages):
    col.page_link(path, label=label)
