"""D3 — Lead scoring engine + documented data-quality rules.

Scoring model (0-100) tuned for the *winback* segment (fans who bought tickets
>=10 months ago). The same engine runs for any segment but the weights are
documented for winback, which is the segment we score by default.

DATA-QUALITY RULES (stated explicitly, never silently fixed):
  R1  tickets_bought_lifetime == -1 is impossible -> treated as missing (0),
      and flagged in a `quality_flag` column. Row is kept.
  R2  months_since_last_purchase blank -> treated as missing, flagged, kept.
  R3  consent_sms / consent_voice blank -> treated as "N" (conservative,
      opt-in required), flagged. Row is kept.
  R4  dnd_registered == "Y" -> outreach channel restricted to email only,
      SMS/voice suppressed. Row is kept.
  R5  Duplicate leads (same name+city) -> both kept but flagged; we assume
      the same person may be re-imported and dedupe at send time, not at
      scoring time.
  R6  days_since_last_contact == 0 -> treated as "contacted today" (valid),
      not reset.
  R7  No row is dropped. Every flagged row is scored and shown.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd


SEGMENTS = ["new_buyer", "winback", "repeat_fan"]


@dataclass
class ScoringWeights:
    # weight (out of 100 total) for each signal
    recency: int = 20          # how long since last purchase / last contact
    engagement: int = 25       # email opens + sms replies + site visits
    intent: int = 20           # cart abandons (high intent signal)
    value: int = 15            # lifetime tickets + avg spend
    contactability: int = 10   # consent + not on DND
    freshness: int = 10        # days since last contact (closer = better)
    _check: int = field(init=False)

    def __post_init__(self):
        self._check = (
            self.recency + self.engagement + self.intent + self.value
            + self.contactability + self.freshness
        )
        assert self._check == 100, f"weights must sum to 100, got {self._check}"


WINBACK_WEIGHTS = ScoringWeights(
    recency=20, engagement=25, intent=20, value=15,
    contactability=10, freshness=10,
)


def _safe_int(val, default=0) -> int:
    try:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return default
        return int(val)
    except (ValueError, TypeError):
        return default


def _clean_row(row: pd.Series) -> tuple[dict, list[str]]:
    """Apply rules R1-R6. Returns cleaned values + quality flags."""
    flags: list[str] = []
    cleaned: dict = {}

    # R1: impossible lifetime tickets
    lt = row.get("tickets_bought_lifetime")
    lt_i = _safe_int(lt, 0)
    if lt_i < 0:
        flags.append("impossible_lifetime_tickets(-1)->0")
        lt_i = 0
    cleaned["tickets_bought_lifetime"] = lt_i

    # R2: missing months since last purchase
    mslp = row.get("months_since_last_purchase")
    mslp_i = _safe_int(mslp, -1)
    if mslp_i < 0:
        flags.append("missing_months_since_last_purchase")
    cleaned["months_since_last_purchase"] = mslp_i

    # R3: blank consent -> "N"
    for c in ("consent_sms", "consent_voice"):
        v = str(row.get(c, "")).strip().upper()
        if v not in ("Y", "N"):
            flags.append(f"blank_{c}->N")
            v = "N"
        cleaned[c] = v

    # R4: DND
    dnd = str(row.get("dnd_registered", "")).strip().upper()
    cleaned["dnd_registered"] = dnd if dnd in ("Y", "N") else "N"

    # numeric engagement signals
    for col in ("email_opens_30d", "sms_replies_30d",
                "site_visits_30d", "cart_abandon_30d"):
        cleaned[col] = _safe_int(row.get(col), 0)

    cleaned["avg_ticket_spend_inr"] = _safe_int(row.get("avg_ticket_spend_inr"), 0)
    cleaned["days_since_last_contact"] = _safe_int(row.get("days_since_last_contact"), 0)
    return cleaned, flags


def _score_one(cleaned: dict, segment: str, w: ScoringWeights) -> dict:
    # Recency: for winback, longer gap is expected; moderate recency is best.
    mslp = cleaned["months_since_last_purchase"]
    if mslp < 0:
        recency_pts = 0.5  # unknown
    elif mslp <= 12:
        recency_pts = 1.0
    elif mslp <= 24:
        recency_pts = 0.7
    else:
        recency_pts = 0.4

    # Engagement: normalise 0-1 across a generous max
    eng = (
        cleaned["email_opens_30d"] * 1.0
        + cleaned["sms_replies_30d"] * 1.5
        + cleaned["site_visits_30d"] * 1.2
    )
    engagement_pts = min(eng / 15.0, 1.0)

    # Intent: cart abandons are a strong buying signal
    intent_pts = min(cleaned["cart_abandon_30d"] / 8.0, 1.0)

    # Value: lifetime tickets + avg spend
    value_pts = min(
        (cleaned["tickets_bought_lifetime"] / 15.0) * 0.5
        + (cleaned["avg_ticket_spend_inr"] / 6000.0) * 0.5,
        1.0,
    )

    # Contactability
    if cleaned["dnd_registered"] == "Y":
        contact_pts = 0.3  # email only
    else:
        contact_pts = 0.0
        if cleaned["consent_sms"] == "Y":
            contact_pts += 0.5
        if cleaned["consent_voice"] == "Y":
            contact_pts += 0.5
        contact_pts = min(contact_pts, 1.0)

    # Freshness: contacted recently is slightly better (stays top of mind)
    dlc = cleaned["days_since_last_contact"]
    if dlc <= 7:
        freshness_pts = 1.0
    elif dlc <= 30:
        freshness_pts = 0.7
    elif dlc <= 90:
        freshness_pts = 0.4
    else:
        freshness_pts = 0.2

    score = round(
        recency_pts * w.recency
        + engagement_pts * w.engagement
        + intent_pts * w.intent
        + value_pts * w.value
        + contact_pts * w.contactability
        + freshness_pts * w.freshness
    )
    score = max(0, min(100, score))

    if score >= 70:
        tier = "A — Hot"
    elif score >= 45:
        tier = "B — Warm"
    else:
        tier = "C — Cold"

    return {
        "score": score,
        "tier": tier,
        "recency_pts": round(recency_pts, 2),
        "engagement_pts": round(engagement_pts, 2),
        "intent_pts": round(intent_pts, 2),
        "value_pts": round(value_pts, 2),
        "contactability_pts": round(contact_pts, 2),
        "freshness_pts": round(freshness_pts, 2),
    }


def recommend_channel(cleaned: dict) -> str:
    if cleaned["dnd_registered"] == "Y":
        return "Email only (DND)"
    if cleaned["consent_sms"] == "Y" and cleaned["consent_voice"] == "Y":
        return "SMS + Voice call"
    if cleaned["consent_sms"] == "Y":
        return "SMS"
    if cleaned["consent_voice"] == "Y":
        return "Voice call"
    return "Email (no SMS/voice consent)"


def score_segment(df: pd.DataFrame, segment: str,
                  weights: ScoringWeights = WINBACK_WEIGHTS) -> pd.DataFrame:
    """Score all rows for the chosen segment. Never drops a row."""
    seg = df[df["segment"] == segment].copy()
    if seg.empty:
        return seg

    # R5: duplicate flag (same name+city)
    dup_mask = seg.duplicated(subset=["name", "city"], keep=False)
    seg["duplicate_flag"] = dup_mask.map({True: "duplicate-name+city", False: ""})

    records = []
    for _, row in seg.iterrows():
        cleaned, flags = _clean_row(row)
        scored = _score_one(cleaned, segment, weights)
        scored["quality_flags"] = "; ".join(flags) if flags else ""
        scored["recommended_channel"] = recommend_channel(cleaned)
        scored["cleaned_lifetime_tickets"] = cleaned["tickets_bought_lifetime"]
        scored["cleaned_consent_sms"] = cleaned["consent_sms"]
        scored["cleaned_consent_voice"] = cleaned["consent_voice"]
        scored["cleaned_dnd"] = cleaned["dnd_registered"]
        records.append(scored)

    scored_df = pd.DataFrame(records, index=seg.index)
    out = pd.concat([seg, scored_df], axis=1)
    out = out.sort_values("score", ascending=False).reset_index(drop=True)
    return out


SCORING_RULES_TEXT = (
    "Scoring model (0-100) for the winback segment.\n"
    "Weights (must sum to 100):\n"
    "  Recency (20): months since last purchase. 0-12mo=1.0, 13-24mo=0.7, 24+mo=0.4, missing=0.5.\n"
    "  Engagement (25): email opens x1 + sms replies x1.5 + site visits x1.2, capped at 15.\n"
    "  Intent (20): cart abandons in 30d, capped at 8.\n"
    "  Value (15): lifetime tickets (0.5) + avg spend INR (0.5), normalised.\n"
    "  Contactability (10): SMS consent +0.5, voice consent +0.5. DND=Y -> 0.3 (email only).\n"
    "  Freshness (10): days since last contact. <=7=1.0, <=30=0.7, <=90=0.4, else 0.2.\n"
    "\n"
    "Tiers: A-Hot >=70, B-Warm >=45, C-Cold <45.\n"
    "\n"
    "Data-quality rules (no row dropped):\n"
    "  R1 tickets_bought_lifetime=-1 -> 0, flagged.\n"
    "  R2 months_since_last_purchase blank -> missing, flagged.\n"
    "  R3 consent blank -> 'N' (opt-in required), flagged.\n"
    "  R4 DND=Y -> email only channel.\n"
    "  R5 duplicate name+city -> both kept, flagged; dedupe at send time.\n"
    "  R6 days_since_last_contact=0 -> 'contacted today', valid.\n"
    "  R7 no row is ever dropped."
)
