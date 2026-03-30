from datetime import date, timedelta

import streamlit as st

from utils.db import init_db, get_sessions, get_eod_logs
from utils.analytics import (
    completion_rate,
    task_alignment_rate,
    total_focused_minutes,
    sessions_by_day,
    top_distractors,
    avg_energy,
    streak_days,
    finished_counts,
)
from utils.style import apply_style, render_topnav

init_db()

st.set_page_config(page_title="Dashboard", page_icon=None, layout="wide")
apply_style()
render_topnav()

st.title("Dashboard")

# ── date range ────────────────────────────────────────────────────────────────
today = date.today()
range_options = {"7 days": 7, "14 days": 14, "30 days": 30, "90 days": 90}
selected_range = st.selectbox(
    "Range",
    list(range_options.keys()),
    index=0,
    label_visibility="collapsed",
)
days_back = range_options[selected_range]
start = (today - timedelta(days=days_back - 1)).isoformat()
end = today.isoformat()

sessions = get_sessions(start, end)
eod_logs = get_eod_logs(start, end)

if not sessions:
    st.caption(f"No sessions in the last {days_back} days.")
    st.stop()

# ── overview metrics ──────────────────────────────────────────────────────────
cols = st.columns(5)
cols[0].metric("Sessions", len(sessions))
cols[1].metric("Completion", f"{completion_rate(sessions):.0%}")
cols[2].metric("Alignment", f"{task_alignment_rate(sessions):.0%}")
cols[3].metric("Focus min", total_focused_minutes(sessions))
cols[4].metric("Streak", f"{streak_days(sessions)}d")

if eod_logs:
    st.caption(f"Avg energy  {avg_energy(eod_logs):.1f} / 5")

st.divider()

# ── sessions per day ──────────────────────────────────────────────────────────
st.subheader("Sessions per day")
try:
    import pandas as pd

    day_counts = sessions_by_day(sessions)
    all_days = [(today - timedelta(days=i)).isoformat() for i in range(days_back - 1, -1, -1)]
    df_days = pd.DataFrame(
        {"date": all_days, "sessions": [day_counts.get(d, 0) for d in all_days]}
    ).set_index("date")
    st.bar_chart(df_days, height=200)
except ImportError:
    st.warning("Install pandas for charts.")

st.divider()

# ── outcomes ──────────────────────────────────────────────────────────────────
st.subheader("Outcomes")
counts = finished_counts(sessions)
c1, c2, c3 = st.columns(3)
c1.metric("Done", counts["yes"])
c2.metric("Partial", counts["partial"])
c3.metric("Missed", counts["no"])

try:
    import pandas as pd

    df_fin = pd.DataFrame(
        {"outcome": ["Done", "Partial", "Missed"],
         "count":   [counts["yes"], counts["partial"], counts["no"]]}
    ).set_index("outcome")
    st.bar_chart(df_fin, height=180)
except ImportError:
    pass

st.divider()

# ── distractors ───────────────────────────────────────────────────────────────
distractors = top_distractors(sessions, n=10)
if distractors:
    st.subheader("Top distractors")
    try:
        import pandas as pd

        df_dist = pd.DataFrame(distractors, columns=["distractor", "count"]).set_index("distractor")
        st.bar_chart(df_dist, height=200)
    except ImportError:
        for name, cnt in distractors:
            st.markdown(f"- **{name}** — {cnt}×")

# ── energy trend ──────────────────────────────────────────────────────────────
if eod_logs:
    st.divider()
    st.subheader("Energy trend")
    try:
        import pandas as pd

        df_e = pd.DataFrame(eod_logs)[["date", "energy"]].set_index("date")
        st.line_chart(df_e, height=180)
    except ImportError:
        for log in eod_logs:
            st.markdown(f"- {log['date']}: {log['energy']}/5")

st.divider()

# ── raw log ───────────────────────────────────────────────────────────────────
with st.expander("Raw session log"):
    try:
        import pandas as pd

        st.dataframe(pd.DataFrame(sessions), use_container_width=True)
    except ImportError:
        for s in sessions:
            st.write(s)
