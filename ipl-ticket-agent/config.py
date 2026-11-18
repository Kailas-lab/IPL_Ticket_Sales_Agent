"""Central configuration: loads env vars and exposes constants."""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2").strip()
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

DATA_DIR = ROOT / "data"
CATALOG_PATH = DATA_DIR / "catalog.json"
LEADS_PATH = DATA_DIR / "leads.csv"


def load_catalog() -> dict:
    with open(CATALOG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


CATALOG = load_catalog()
