"""Sales agent: catalog-grounded Q&A + personalised outreach generation.

Tries the Hugging Face LLM first. If no token or the call fails, it uses a
deterministic rule-based answer built from the catalog so the app is always
useful.
"""
from __future__ import annotations

import re

from config import CATALOG
from core.llm import LLMClient, catalog_context, chat_prompt, outreach_prompt
from core.lead_scorer import recommend_channel  # noqa: F401  (re-export friendly)


_client = LLMClient()


# --- Rule-based fallback -----------------------------------------------------

def _fallback_answer(question: str) -> str:
    q = question.lower()

    def match_any(keywords: list[str]) -> bool:
        return any(k in q for k in keywords)

    # price / ticket cost
    if match_any(["price", "cost", "how much", "rate", "ticket rate"]):
        lines = ["Here are the ticket prices (INR) by stand and match:"]
        for a in CATALOG["seat_areas"]:
            prices = ", ".join(
                f"{m['id']} ({m['opponent']} {m['date']}): {p}"
                for m in CATALOG["matches"]
                for k, p in a["price_inr_by_match"].items()
                if k == m["id"]
            )
            lines.append(f"- {a['name']}: {prices}")
        lines.append("Early Bird (14 days before match) gives 15% off. Students get "
                     "the North Stand for 500 INR with a valid ID.")
        return "\n".join(lines)

    # matches / schedule
    if match_any(["match", "schedule", "fixture", "when", "date", "game"]):
        lines = [f"{CATALOG['team']} home matches for {CATALOG['season']}:"]
        for m in CATALOG["matches"]:
            lines.append(f"- {m['opponent']} on {m['date']} at {m['time']} ({m['day']})")
        return "\n".join(lines)

    # children
    if match_any(["child", "kid", "minor", "infant"]):
        f = next(x for x in CATALOG["faq"] if x["id"] == "child-ticket")
        return f["answer"]

    # parking (not published -> honest answer)
    if match_any(["park", "vehicle", "car park"]):
        return ("Parking information is not published. We strongly recommend using "
                "public transport — the stadium is a short walk from Churchgate "
                "station. Corporate box holders receive parking instructions "
                "separately. For any other parking question please contact the "
                "box office.")

    # refund
    if match_any(["refund", "cancel", "money back"]):
        return ("The only published refund is for a fully rained-out match "
                "(no ball bowled) — processed automatically within 10 working "
                "days. For any other refund situation please contact the box "
                "office; the team handles these case by case.")

    # accessibility
    if match_any(["wheelchair", "disab", "accessib", "mobility"]):
        return ("Accessibility information is not currently published. Please "
                "email the box office — wheelchair bays in the East Pavilion "
                "are allocated on a first-come basis with a companion seat at "
                "no extra cost.")

    # offers
    if match_any(["offer", "discount", "deal", "promo", "student", "winback"]):
        lines = ["Current offers:"]
        for o in CATALOG["offers"]:
            lines.append(f"- {o['name']}: {o['rule']}")
        return "\n".join(lines)

    # venue
    if match_any(["venue", "stadium", "where", "location", "address"]):
        return f"Home venue: {CATALOG['home_venue']}."

    # FAQ keyword scan
    for item in CATALOG["faq"]:
        words = item["question"].lower().split()
        if any(w in q for w in words if len(w) > 3):
            return item["answer"]

    return ("I'm not sure about that. I can help with match schedules, ticket "
            "prices, offers, child tickets, entry rules, and rain policy. For "
            "anything else please contact the Mumbai Marvels box office.")


# --- Public API --------------------------------------------------------------

def answer_question(question: str) -> tuple[str, str]:
    """Return (answer_text, source) where source is 'LLM' or 'rules'."""
    if not question.strip():
        return ("Please ask a question about tickets, matches, prices, or offers.",
                "rules")
    if _client.available:
        ctx = catalog_context()
        out = _client.generate(chat_prompt(question, ctx), max_new_tokens=300)
        if out:
            return out, "LLM (Hugging Face)"
    return _fallback_answer(question), "rule-based fallback"


def generate_outreach(lead_row: dict, score: int, tier: str, offer: str) -> str:
    if _client.available:
        out = _client.generate(
            outreach_prompt(lead_row, score, tier, offer), max_new_tokens=120
        )
        if out:
            return out
    return _fallback_outreach(lead_row, score, tier, offer)


def _fallback_outreach(lead_row: dict, score: int, tier: str, offer: str) -> str:
    name = str(lead_row.get("name", "there")).split()[0]
    segment = lead_row.get("segment", "fan")
    if segment == "winback":
        opener = "We've missed you at Wankhede this season"
    elif segment == "repeat_fan":
        opener = "Thank you for being one of our most loyal Mumbai Marvels fans"
    else:
        opener = "Welcome to the Mumbai Marvels family"
    offer_line = ""
    if offer:
        offer_line = f" Special offer for you: {offer}."
    return (
        f"Hi {name}, {opener}! {offer_line} "
        f"Home matches for IPL 2027 are live now — from the North Stand at "
        f"1,500 INR to the Corporate Box at 7,500 INR. "
        f"Book 14 days early for 15% off. Reply MARVELS to grab your seats. "
        f"— Mumbai Marvels"
    )


def llm_status() -> dict:
    return {
        "available": _client.available,
        "model": _client.url.split("/models/")[-1] if _client.available else "n/a",
        "mode": "LLM (Hugging Face Inference API)" if _client.available
        else "rule-based fallback (set HF_TOKEN in .env for LLM mode)",
    }
