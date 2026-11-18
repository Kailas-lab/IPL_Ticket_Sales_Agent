"""Lead scoring page (D3): pick a segment, view scored table, rules, outreach."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from config import CATALOG, LEADS_PATH
from core.lead_scorer import (
    SCORING_RULES_TEXT,
    SEGMENTS,
    score_segment,
)
from core.sales_agent import generate_outreach
from ui.styles import apply_theme, card, kpi, tier_badge


def render():
    apply_theme()
    st.markdown("## Lead Scoring (D3)")
    st.caption("Score one segment's 20 leads. Imperfect rows are flagged, never dropped.")

    df = pd.read_csv(LEADS_PATH)
    segment = st.selectbox("Choose a segment", SEGMENTS, index=SEGMENTS.index("winback"))

    scored = score_segment(df, segment)

    # KPIs
    a = (scored["tier"].str.startswith("A")).sum()
    b = (scored["tier"].str.startswith("B")).sum()
    c = (scored["tier"].str.startswith("C")).sum()
    flagged = (scored["quality_flags"] != "").sum()
    dups = (scored["duplicate_flag"] != "").sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi(str(a), "A — Hot")
    with c2:
        kpi(str(b), "B — Warm")
    with c3:
        kpi(str(c), "C — Cold")
    with c4:
        kpi(str(flagged), "Flagged rows")
    with c5:
        kpi(str(dups), "Duplicates")

    with st.expander("Scoring rules & data-quality policy"):
        st.code(SCORING_RULES_TEXT, language="text")

    st.markdown("### Scored leads")
    show_cols = [
        "lead_id", "name", "city", "score", "tier", "recommended_channel",
        "recency_pts", "engagement_pts", "intent_pts", "value_pts",
        "contactability_pts", "freshness_pts",
        "quality_flags", "duplicate_flag",
    ]
    display = scored[show_cols].copy()
    st.dataframe(display, use_container_width=True, hide_index=True, height=420)

    st.markdown("### Generate outreach for a lead")
    lead_ids = scored["lead_id"].tolist()
    chosen = st.selectbox("Pick a lead", lead_ids,
                          format_func=lambda lid: f"{lid} — {scored.loc[scored['lead_id']==lid,'name'].iloc[0]}")
    row = scored[scored["lead_id"] == chosen].iloc[0]

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(
            f'<div class="mm-card">'
            f'<b>{row["name"]}</b> ({row["city"]})<br>'
            f'Score: <b style="color:#f5b502">{row["score"]}/100</b> '
            f'{tier_badge(row["tier"])}<br>'
            f'Channel: {row["recommended_channel"]}<br>'
            f'<span class="mm-muted">Lifetime tickets: '
            f'{row["cleaned_lifetime_tickets"]}</span><br>'
            f'<span class="mm-muted">Avg spend: '
            f'{row["avg_ticket_spend_inr"]} INR</span><br>'
            f'<span class="mm-muted">DND: {row["cleaned_dnd"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        offer = st.selectbox("Offer to highlight",
                             [""] + [o["name"] + " — " + o["rule"] for o in CATALOG["offers"]])
        if st.button("Generate outreach message", type="primary"):
            lead_row = row.to_dict()
            msg = generate_outreach(lead_row, int(row["score"]), row["tier"], offer)
            st.markdown("#### Draft message")
            card(f"<span style='white-space:pre-wrap'>{msg}</span>")

    st.markdown("### Data-quality notes")
    notes = []
    if (scored["quality_flags"] != "").any():
        notes.append("Some rows had data issues (impossible values, missing consent, "
                     "missing purchase date). Each is flagged in the table and kept.")
    if (scored["duplicate_flag"] != "").any():
        notes.append("Duplicate name+city pairs detected. Both kept and flagged; "
                     "dedupe should happen at send time, not at scoring time.")
    if not notes:
        notes.append("No data-quality issues detected in this segment.")
    for n in notes:
        st.markdown(f"- {n}")
