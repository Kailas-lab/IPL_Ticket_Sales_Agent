"""Shared CSS / theme helpers for a premium Streamlit look."""
from __future__ import annotations

import streamlit as st

THEME_CSS = """
<style>
    :root {
        --mm-navy: #0a1f44;
        --mm-blue: #1d4ed8;
        --mm-gold: #f5b502;
        --mm-sky:  #38bdf8;
        --mm-bg:   #0b1220;
        --mm-card: #111b33;
        --mm-muted:#94a3b8;
    }
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    }
    .stApp {
        background:
            radial-gradient(1200px 600px at 80% -10%, rgba(56,189,248,0.10), transparent),
            radial-gradient(900px 500px at -10% 20%, rgba(29,78,216,0.12), transparent),
            linear-gradient(180deg, #0b1220 0%, #0a1124 100%);
        color: #e6edf7;
    }
    /* Cards */
    .mm-card {
        background: linear-gradient(180deg, rgba(20,30,55,0.85), rgba(13,20,40,0.85));
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        backdrop-filter: blur(6px);
    }
    .mm-kpi {
        background: linear-gradient(135deg, rgba(29,78,216,0.22), rgba(56,189,248,0.12));
        border: 1px solid rgba(56,189,248,0.25);
        border-radius: 14px;
        padding: 14px 16px;
        text-align: center;
    }
    .mm-kpi .num { font-size: 28px; font-weight: 800; color: #f5b502; }
    .mm-kpi .lbl { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .08em; }
    .mm-badge {
        display:inline-block; padding:3px 10px; border-radius:999px;
        font-size:12px; font-weight:700;
    }
    .mm-badge-A { background: rgba(245,181,2,0.18); color:#f5b502; border:1px solid rgba(245,181,2,0.5); }
    .mm-badge-B { background: rgba(56,189,248,0.18); color:#7dd3fc; border:1px solid rgba(56,189,248,0.5); }
    .mm-badge-C { background: rgba(148,163,184,0.18); color:#cbd5e1; border:1px solid rgba(148,163,184,0.5); }
    .mm-hero {
        background: linear-gradient(120deg, rgba(10,31,68,0.95), rgba(29,78,216,0.45));
        border:1px solid rgba(56,189,248,0.25);
        border-radius:20px; padding:28px 30px; margin-bottom:8px;
    }
    .mm-hero h1 { color:#fff; margin:0; font-weight:800; letter-spacing:-.02em; }
    .mm-hero p { color:#c7d2fe; margin-top:8px; font-size:16px; }
    .mm-chip {
        display:inline-block; margin-right:6px; padding:2px 10px; border-radius:8px;
        background: rgba(56,189,248,0.12); color:#7dd3fc; font-size:12px;
        border:1px solid rgba(56,189,248,0.3);
    }
    .mm-flag { color:#fca5a5; font-size:12px; }
    .mm-muted { color:#94a3b8; }
    .stSidebar { background: rgba(8,14,28,0.96); border-right:1px solid rgba(56,189,248,0.15); }
    .stSidebar .stRadio > label { color:#e6edf7; }
    section[data-testid="stSidebar"] * { color:#dbe4f3; }
    .stMetric label { color:#94a3b8 !important; }
    .stMetric-value { color:#f5b502 !important; }
    /* data frame */
    .stDataFrame { color:#e6edf7; }
    /* buttons */
    .stButton > button {
        border-radius:10px; border:1px solid rgba(56,189,248,0.4);
        background:linear-gradient(180deg, rgba(29,78,216,0.6), rgba(29,78,216,0.35));
        color:#fff; font-weight:600;
    }
    .stButton > button:hover {
        background:linear-gradient(180deg, rgba(56,189,248,0.6), rgba(29,78,216,0.45));
        border-color: rgba(245,181,2,0.6);
    }
    hr.mm-div { border:0; border-top:1px solid rgba(56,189,248,0.18); margin:18px 0; }
</style>
"""


def apply_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def card(body: str):
    st.markdown(f'<div class="mm-card">{body}</div>', unsafe_allow_html=True)


def kpi(value: str, label: str):
    st.markdown(
        f'<div class="mm-kpi"><div class="num">{value}</div>'
        f'<div class="lbl">{label}</div></div>',
        unsafe_allow_html=True,
    )


def tier_badge(tier: str) -> str:
    code = tier.strip()[0]
    return f'<span class="mm-badge mm-badge-{code}">{tier}</span>'
