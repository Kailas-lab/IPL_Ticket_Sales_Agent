"""Sales chat page: fan Q&A powered by the Hugging Face LLM (+ fallback)."""
from __future__ import annotations

import streamlit as st

from core.sales_agent import answer_question, llm_status
from ui.styles import apply_theme, card


def render():
    apply_theme()
    st.markdown("## AI Sales Chat")
    status = llm_status()
    mode_color = "#22c55e" if status["available"] else "#f5b502"
    st.markdown(
        f'<span class="mm-muted">Engine:</span> '
        f'<span style="color:{mode_color}">{status["mode"]}</span>',
        unsafe_allow_html=True,
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # suggested questions
    st.markdown("##### Try asking")
    chips = [
        "What matches are at Wankhede this season?",
        "How much is the Corporate Box vs Chennai?",
        "Do children need a ticket?",
        "Is there parking at the stadium?",
        "What's the refund policy?",
        "I'm a returning fan, any offers for me?",
    ]
    cols = st.columns(3)
    for i, chip in enumerate(chips):
        if cols[i % 3].button(chip, key=f"chip_{i}"):
            st.session_state["pending_question"] = chip

    # render history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("source"):
                st.caption(f"Source: {msg['source']}")

    # input
    question = st.chat_input("Ask about matches, prices, offers, kids, accessibility...")
    if not question and "pending_question" in st.session_state:
        question = st.session_state.pop("pending_question")

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, source = answer_question(question)
            st.markdown(answer)
            st.caption(f"Source: {source}")
        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer, "source": source}
        )

    with st.expander("About this chat"):
        card(
            "<span class='mm-muted'>Answers are grounded in the Mumbai Marvels "
            "catalog. For topics the team does not publish (parking, refunds, "
            "accessibility), the agent gives a safe, honest deflection to the "
            "box office. Set a free </span><b>HF_TOKEN</b><span class='mm-muted'> "
            "in .env to switch from rule-based fallback to the Hugging Face "
            "Inference API LLM.</span>"
        )
