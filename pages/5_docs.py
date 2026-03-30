import streamlit as st
from utils.style import apply_style, render_topnav

st.set_page_config(page_title="Docs", page_icon=None)
apply_style()
render_topnav()

st.title("Docs")
st.caption("How to use the app, what each field means, and why it's built this way.")

st.divider()

# ── philosophy ────────────────────────────────────────────────────────────────
st.subheader("Philosophy")
st.markdown("""
ADHD makes two things hard: **starting** and **staying on track**.

This app doesn't try to be a full productivity system. It does three things:

1. **Reduce start friction** — one field, one button. No project trees, no tags, no priorities.
2. **Surface drift** — by asking what you *actually* worked on after the fact, patterns of task-switching become visible over time.
3. **Close the day** — a short end-of-day log creates a natural stopping point and builds a record of wins, which is easy to forget with ADHD.
""")

st.divider()

# ── pages ─────────────────────────────────────────────────────────────────────
st.subheader("Pages")

with st.expander("Timer"):
    st.markdown("""
**What it does:** Starts a focus session and tracks elapsed time. On stop, it prompts a short log.

**Fields:**
- **What are you working on?** — Declare your intent before starting. This is your *commitment*.
- **What actually happened?** — Filled after the session. If you drifted, write what you actually did. This is where the data gets interesting.
- **Finished?** — `yes` / `partial` / `no`. Be honest. Partial is fine.
- **Distractor** — What pulled you away, if anything. Over time, patterns appear in the dashboard.

**How the timer works:** Start time is stored when you click Start. Elapsed is computed on each re-render — no background threads. Pause accumulates elapsed seconds so resume continues from where you left off.
""")

with st.expander("Check-in"):
    st.markdown("""
**What it does:** A mid-day snapshot. Log a session manually (e.g. if you forgot to use the timer), check your energy, and review what's been done today.

**Energy slider** — A quick 1–5 pulse. Not saved to the database; just a prompt to check in with yourself. If you're at 1–2, the app suggests a break.

**Session list** — Shows today's sessions in reverse order. Each one can be expanded to see drift and distractor details, or deleted if logged by mistake.
""")

with st.expander("End of day"):
    st.markdown("""
**What it does:** A short reflection to close the day. Takes under 2 minutes.

**Fields:**
- **Overall energy** — How did you feel across the whole day, not just right now.
- **Sessions completed** — Auto-filled from today's data. Adjust if needed.
- **Biggest win** — Forces you to name something good. Crucial for ADHD where the day can feel like a failure even when it wasn't.
- **Biggest hijack** — What stole the most focus. Naming it reduces its power tomorrow.
- **Notes** — Anything else: blockers, how you feel, what to tackle first tomorrow.

Submitting again on the same day updates the existing record (no duplicates).
""")

with st.expander("Dashboard"):
    st.markdown("""
**What it does:** Shows trends across the last 7, 14, 30, or 90 days.

**Metrics:**
| Metric | Definition |
|---|---|
| Sessions | Total logged sessions in range |
| Completion | % of sessions marked `yes` |
| Alignment | % where declared task = actual task |
| Focus min | Sum of all session durations |
| Streak | Consecutive calendar days with at least one session |

**Charts:** Sessions per day, outcome breakdown (done/partial/missed), top distractors by frequency, energy trend from EOD logs.
""")

st.divider()

# ── data ──────────────────────────────────────────────────────────────────────
st.subheader("Your data")
st.markdown("""
Everything is stored in a local SQLite file (`focus.db`) in the project directory. Nothing is sent anywhere. There is no account, no sync, no cloud.

To back up your data, copy `focus.db`. To reset, delete it — `init_db()` will recreate the schema on next launch.
""")
