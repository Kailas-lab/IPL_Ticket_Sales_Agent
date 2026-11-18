"""Catalog page: matches, seat areas & prices, FAQ, offers, not-published."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from config import CATALOG
from ui.styles import apply_theme, card


def render():
    apply_theme()
    st.markdown(f"## {CATALOG['team']} — Ticket Catalog (D2)")
    st.caption(f"{CATALOG['season']} · {CATALOG['home_venue']}")

    # Matches
    st.markdown("### Home matches")
    match_rows = []
    for m in CATALOG["matches"]:
        match_rows.append({
            "Match": m["id"],
            "Opponent": m["opponent"],
            "Date": m["date"],
            "Day": m["day"],
            "Time": m["time"],
            "Type": m["type"],
            "Stands open": ", ".join(m["seat_areas_available"]),
        })
    st.dataframe(pd.DataFrame(match_rows), use_container_width=True, hide_index=True)

    # Seat areas + price matrix
    st.markdown("### Seat areas & prices (INR)")
    price_rows = []
    for a in CATALOG["seat_areas"]:
        row = {"Area": f"{a['id']} — {a['name']}"}
        for m in CATALOG["matches"]:
            row[m["id"]] = a["price_inr_by_match"].get(m["id"], "—")
        price_rows.append(row)
    st.dataframe(pd.DataFrame(price_rows), use_container_width=True, hide_index=True)

    st.markdown("### Stand descriptions")
    for a in CATALOG["seat_areas"]:
        card(f"<b>{a['name']}</b><br><span class='mm-muted'>{a['description']}</span>")
        st.markdown("")

    # Offers
    st.markdown("### Active offers")
    for o in CATALOG["offers"]:
        card(f"<b>{o['name']}</b><br><span class='mm-muted'>{o['rule']}</span>")
        st.markdown("")

    # FAQ
    st.markdown("### FAQ")
    for f in CATALOG["faq"]:
        with st.expander(f["question"]):
            st.write(f["answer"])

    # Not published
    st.markdown("### Topics the team does NOT publish")
    st.caption("Honest about the gaps. The agent gives a safe, deflecting answer for these.")
    for n in CATALOG["not_published"]:
        card(
            f"<b>{n['topic']}</b> "
            f"<span class='mm-flag'>(not published)</span><br>"
            f"<span class='mm-muted'>{n['assumption']}</span>"
        )
        st.markdown("")
