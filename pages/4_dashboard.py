"""Analytics dashboard."""
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

init_db()

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Focus Dashboard")

# ── date range picker ─────────────────────────────────────────────────────────
today = date.today()
range_options = {
    "Last 7 days": 7,
    "Last 14 days": 14,
    "Last 30 days": 30,
    "Last 90 days": 90,
}
selected_range = st.selectbox("Date range", list(range_options.keys()), index=0)
days_back = range_options[selected_range]
start = (today - timedelta(days=days_back - 1)).isoformat()
end = today.isoformat()

sessions = get_sessions(start, end)
eod_logs = get_eod_logs(start, end)

if not sessions:
    st.info(f"No sessions recorded in the last {days_back} days. Start your first focus session!")
    st.stop()

# ── top-level metrics ─────────────────────────────────────────────────────────
st.subheader("Overview")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total sessions", len(sessions))
c2.metric("Completion rate", f"{completion_rate(sessions):.0%}")
c3.metric("Alignment rate", f"{task_alignment_rate(sessions):.0%}")
c4.metric("Focus minutes", total_focused_minutes(sessions))
c5.metric("Current streak", f"{streak_days(sessions)} days")

if eod_logs:
    c_e = st.columns(1)[0]
    c_e.metric("Avg energy (EOD)", f"{avg_energy(eod_logs):.1f} / 5")

st.divider()

# ── sessions per day bar chart ────────────────────────────────────────────────
st.subheader("Sessions per day")
try:
    import pandas as pd

    day_counts = sessions_by_day(sessions)
    # fill missing days with 0
    all_days = [(today - timedelta(days=i)).isoformat() for i in range(days_back - 1, -1, -1)]
    df_days = pd.DataFrame({"date": all_days, "sessions": [day_counts.get(d, 0) for d in all_days]})
    df_days = df_days.set_index("date")
    st.bar_chart(df_days)
except ImportError:
    st.warning("Install pandas for charts: `pip install pandas`")

st.divider()

# ── finished breakdown ────────────────────────────────────────────────────────
st.subheader("Session outcomes")
counts = finished_counts(sessions)
col_a, col_b, col_c = st.columns(3)
col_a.metric("✅ Finished", counts["yes"])
col_b.metric("🔶 Partial", counts["partial"])
col_c.metric("❌ Not finished", counts["no"])

try:
    import pandas as pd

    df_fin = pd.DataFrame(
        {"outcome": ["Finished", "Partial", "Not finished"], "count": [counts["yes"], counts["partial"], counts["no"]]}
    ).set_index("outcome")
    st.bar_chart(df_fin)
except ImportError:
    pass

st.divider()

# ── distractors ───────────────────────────────────────────────────────────────
distractors = top_distractors(sessions, n=10)
if distractors:
    st.subheader("Top distractors")
    try:
        import pandas as pd

        df_dist = pd.DataFrame(distractors, columns=["Distractor", "Count"]).set_index("Distractor")
        st.bar_chart(df_dist)
    except ImportError:
        for name, cnt in distractors:
            st.markdown(f"- **{name}**: {cnt}x")

st.divider()

# ── energy trend ──────────────────────────────────────────────────────────────
if eod_logs:
    st.subheader("Energy trend (EOD)")
    try:
        import pandas as pd

        df_energy = pd.DataFrame(eod_logs)[["date", "energy"]].set_index("date")
        st.line_chart(df_energy)
    except ImportError:
        for log in eod_logs:
            st.markdown(f"- {log['date']}: {log['energy']}/5")

st.divider()

# ── raw session log ───────────────────────────────────────────────────────────
with st.expander("Raw session log"):
    try:
        import pandas as pd

        df_raw = pd.DataFrame(sessions)
        st.dataframe(df_raw, use_container_width=True)
    except ImportError:
        for s in sessions:
            st.write(s)
