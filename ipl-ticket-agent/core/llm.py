"""Hugging Face Inference API wrapper with a graceful rule-based fallback.

The app works even with no token (fallback mode) so it is fully functional
out of the box. When a free HF token is provided in .env, real LLM responses
are used for richer chat and outreach copy.
"""
from __future__ import annotations

import requests

from config import CATALOG, HF_API_URL, HF_TOKEN


class LLMClient:
    """Thin wrapper around the HF Inference API text-generation endpoint."""

    def __init__(self, token: str | None = None, model_url: str | None = None):
        self.token = (token or HF_TOKEN).strip()
        self.url = model_url or HF_API_URL
        self.available = bool(self.token)

    def generate(self, prompt: str, max_new_tokens: int = 400) -> str:
        if not self.available:
            return ""
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False,
            },
        }
        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 503:
                # Model warming up on HF side — fall back gracefully.
                return ""
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and data:
                return data[0].get("generated_text", "").strip()
            return ""
        except Exception:
            return ""


# --- Prompt builders ---------------------------------------------------------

def chat_prompt(user_question: str, context: str) -> str:
    sys = (
        "You are the official AI sales assistant for the Mumbai Marvels IPL team. "
        "Answer the fan's question using ONLY the provided catalog context. "
        "Be friendly, concise, and practical. If the answer is not in the context, "
        "say you do not have that information and suggest contacting the box office. "
        "Never invent prices, dates, or policies. Prices are in INR."
    )
    return (
        f"<s>[INST] {sys}\n\n"
        f"CATALOG CONTEXT:\n{context}\n\n"
        f"FAN QUESTION: {user_question} [/INST]"
    )


def outreach_prompt(lead_row: dict, score: int, tier: str, offer: str) -> str:
    sys = (
        "You are a CRM copywriter for the Mumbai Marvels IPL team. "
        "Write a short, warm, personalised outreach message to a fan lead. "
        "Maximum 80 words. Mention the most relevant offer if any. "
        "Do not make promises the team cannot keep. End with one clear call to action."
    )
    lead_summary = (
        f"name={lead_row.get('name')}, city={lead_row.get('city')}, "
        f"segment={lead_row.get('segment')}, "
        f"lifetime_tickets={lead_row.get('tickets_bought_lifetime')}, "
        f"last_purchase_months_ago={lead_row.get('months_since_last_purchase')}, "
        f"avg_spend_inr={lead_row.get('avg_ticket_spend_inr')}, "
        f"score={score}/100, tier={tier}"
    )
    return (
        f"<s>[INST] {sys}\n\n"
        f"LEAD: {lead_summary}\n"
        f"RELEVANT OFFER: {offer}\n"
        f"Write the message. [/INST]"
    )


# --- Shared catalog context for the LLM --------------------------------------

def catalog_context() -> str:
    lines: list[str] = []
    lines.append(f"Team: {CATALOG['team']} ({CATALOG['season']})")
    lines.append(f"Home venue: {CATALOG['home_venue']}")
    lines.append("\nMatches:")
    for m in CATALOG["matches"]:
        lines.append(
            f"  {m['id']}: vs {m['opponent']} on {m['date']} at {m['time']} "
            f"({m['day']}, {m['type']})"
        )
    lines.append("\nSeat areas & prices (INR):")
    for a in CATALOG["seat_areas"]:
        prices = ", ".join(f"{k}={v}" for k, v in a["price_inr_by_match"].items())
        lines.append(f"  {a['id']} {a['name']}: {prices}. {a['description']}")
    lines.append("\nFAQ:")
    for f in CATALOG["faq"]:
        lines.append(f"  Q: {f['question']}")
        lines.append(f"  A: {f['answer']}")
    lines.append("\nOffers:")
    for o in CATALOG["offers"]:
        lines.append(f"  {o['name']}: {o['rule']}")
    return "\n".join(lines)
