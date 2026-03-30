import streamlit as st

_CSS = """
<style>
/* ── layout ──────────────────────────────────────────────── */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 780px;
}

/* ── typography ──────────────────────────────────────────── */
h1 {
    font-size: 1.6rem !important;
    font-weight: 500 !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 0.1rem !important;
}
h2 {
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    letter-spacing: -0.02em !important;
    color: #333 !important;
}
h3 {
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #888 !important;
}
p, label, .stMarkdown { color: #333; }

/* ── buttons ─────────────────────────────────────────────── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #ccc !important;
    border-radius: 4px !important;
    color: #111 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 0.45rem 1rem !important;
    transition: background 0.12s, border-color 0.12s, color 0.12s !important;
    box-shadow: none !important;
}
.stButton > button:hover:not(:disabled) {
    background: #111 !important;
    border-color: #111 !important;
    color: #F7F6F2 !important;
}
.stButton > button:disabled {
    opacity: 0.25 !important;
    cursor: not-allowed !important;
}

/* ── form submit ─────────────────────────────────────────── */
.stFormSubmitButton > button {
    background: #111 !important;
    border: 1px solid #111 !important;
    border-radius: 4px !important;
    color: #F7F6F2 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 0.45rem 1.4rem !important;
    box-shadow: none !important;
}
.stFormSubmitButton > button:hover {
    background: #333 !important;
    border-color: #333 !important;
}

/* ── metric cards ────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #EEECEA;
    border-radius: 6px;
    padding: 1rem 1.1rem 0.8rem;
    border: none;
}
[data-testid="metric-container"] label {
    font-size: 0.7rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #888 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 500 !important;
    color: #111 !important;
}

/* ── divider ─────────────────────────────────────────────── */
hr {
    border-color: #DDD !important;
    margin: 1.6rem 0 !important;
}

/* ── inputs ──────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    border-color: #DDD !important;
    border-radius: 4px !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #111 !important;
    box-shadow: none !important;
}

/* ── expander ────────────────────────────────────────────── */
.streamlit-expanderHeader {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #555 !important;
    border-bottom: 1px solid #EEE !important;
}
details[data-testid="stExpander"] {
    border: 1px solid #E4E2DE !important;
    border-radius: 6px !important;
    background: #FAFAF8 !important;
}

/* ── alerts / info ───────────────────────────────────────── */
.stAlert {
    border-radius: 6px !important;
    border-left-width: 3px !important;
    font-size: 0.85rem !important;
}

/* ── sidebar nav ─────────────────────────────────────────── */
[data-testid="stSidebarNav"] a span {
    font-size: 0.85rem !important;
    letter-spacing: 0.01em !important;
}

/* ── page links ──────────────────────────────────────────── */
[data-testid="stPageLink-NavLink"] {
    display: block !important;
    border: 1px solid #111 !important;
    border-radius: 4px !important;
    padding: 0.55rem 1.2rem !important;
    background: #111 !important;
    text-decoration: none !important;
    transition: background 0.12s !important;
}
[data-testid="stPageLink-NavLink"]:hover {
    background: #333 !important;
    border-color: #333 !important;
}
[data-testid="stPageLink-NavLink"] p {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #F7F6F2 !important;
    margin: 0 !important;
}

/* secondary links (in columns) */
.stColumns [data-testid="stPageLink-NavLink"] {
    background: transparent !important;
    border-color: #DDD !important;
    padding: 0.4rem 0.7rem !important;
}
.stColumns [data-testid="stPageLink-NavLink"]:hover {
    border-color: #111 !important;
    background: #EEECEA !important;
}
.stColumns [data-testid="stPageLink-NavLink"] p {
    color: #555 !important;
    font-size: 0.75rem !important;
}

/* ── hide Streamlit branding (not header — sidebar lives there) ── */
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }
</style>
"""


def apply_style() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def status_badge(finished: str) -> str:
    """Return an HTML inline badge for session finished status."""
    cfg = {
        "yes":     ("#D4EDD4", "#2D6A2D", "done"),
        "partial": ("#FDF3DC", "#7A5800", "partial"),
        "no":      ("#F5E0E0", "#8B2020", "missed"),
    }
    bg, fg, label = cfg.get(finished, ("#EEE", "#555", finished))
    return (
        f"<span style='background:{bg};color:{fg};padding:1px 7px;"
        f"border-radius:3px;font-size:0.7rem;font-weight:600;"
        f"letter-spacing:0.05em;text-transform:uppercase'>{label}</span>"
    )
