"""Home page: hero, KPIs, how-it-works."""
from __future__ import annotations

import streamlit as st

from config import CATALOG
from core.sales_agent import llm_status
from ui.styles import card, kpi, apply_theme


def render():
    apply_theme()
    st.markdown(
        f"""
        <div class="mm-hero">
            <h1>{CATALOG['team']} — AI Ticket Sales Agent</h1>
            <p>{CATALOG['season']} &middot; Home: {CATALOG['home_venue']}</p>
            <p style="margin-top:10px;">
                <span class="mm-chip">Catalog Q&amp;A</span>
                <span class="mm-chip">Lead scoring</span>
                <span class="mm-chip">Personalised outreach</span>
                <span class="mm-chip">Free LLM (Hugging Face)</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status = llm_status()
    mode_color = "#22c55e" if status["available"] else "#f5b502"
    st.markdown(
        f'<div class="mm-card" style="margin-bottom:14px;">'
        f'<b>Engine status:</b> <span style="color:{mode_color}">{status["mode"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### At a glance")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi(str(len(CATALOG["matches"])), "Home matches")
    with c2:
        kpi(str(len(CATALOG["seat_areas"])), "Seat areas")
    with c3:
        kpi(str(len(CATALOG["faq"])), "FAQ items")
    with c4:
        kpi(str(len(CATALOG["offers"])), "Active offers")

    st.markdown("### How this agent works")
    card(
        "<b>1. Catalog (D2)</b> — an invented Mumbai Marvels catalog: matches, "
        "seat areas, prices, FAQ, offers, and three deliberately unpublished "
        "topics (parking, refunds, accessibility). The agent answers fans only "
        "from this catalog."
    )
    st.markdown("")
    card(
        "<b>2. Lead scoring (D3)</b> — choose a segment (new_buyer, winback, or "
        "repeat_fan). Every lead is scored 0-100 with stated data-quality rules. "
        "Imperfect rows are flagged, never dropped."
    )
    st.markdown("")
    card(
        "<b>3. AI sales chat</b> — fans ask about matches, prices, kids, offers. "
        "A free Hugging Face LLM answers; if no token is set, a rule-based "
        "fallback grounded in the catalog keeps the agent fully functional."
    )
    st.markdown("")
    card(
        "<b>4. Outreach</b> — pick a scored lead and generate a personalised, "
        "compliant (DND-aware) outreach message in one click."
    )

    st.markdown("### Quick links")
    st.caption("Use the sidebar to switch between the catalog, lead scoring, and sales chat views.")
