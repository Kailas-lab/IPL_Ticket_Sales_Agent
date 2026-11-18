"""Mumbai Marvels — IPL Ticket Sales Agent (Streamlit app).

Run:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from core.sales_agent import llm_status
from ui.styles import apply_theme
from ui.page_home import render as render_home
from ui.page_catalog import render as render_catalog
from ui.page_leads import render as render_leads
from ui.page_chat import render as render_chat

st.set_page_config(
    page_title="Mumbai Marvels — AI Ticket Sales Agent",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

PAGES = {
    "Home": render_home,
    "Catalog (D2)": render_catalog,
    "Lead Scoring (D3)": render_leads,
    "Sales Chat": render_chat,
}

with st.sidebar:
    st.markdown("## 🏏 Mumbai Marvels")
    st.caption("AI Ticket Sales Agent")
    status = llm_status()
    dot = "🟢" if status["available"] else "🟡"
    st.caption(f"{dot} {status['mode']}")
    st.markdown("---")
    choice = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
    st.markdown("---")
    st.caption("Powered by a free Hugging Face LLM with a rule-based fallback. "
               "All data is synthetic/assumed.")

PAGES[choice]()
