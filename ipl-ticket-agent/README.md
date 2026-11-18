# Mumbai Marvels — AI Ticket Sales Agent

An AI-powered sales agent for an invented IPL team ("Mumbai Marvels") that:

1. **Answers fan questions** from a team catalog (matches, prices, FAQ, offers).
2. **Scores sales leads** from `data/leads.csv` with a transparent, documented model.
3. **Generates personalised, DND-aware outreach** messages.
4. Uses a **free Hugging Face LLM** with a fully working **rule-based fallback**.

Built with **Streamlit** for an attractive, production-style UI. All data is
synthetic / assumed. English only.

---

## Folder structure

```
ipl-ticket-agent/
├── app.py                      # Streamlit entry point (sidebar nav + routing)
├── requirements.txt
├── README.md                   # this file
├── .env.example                # copy to .env and add your free HF token
├── config.py                   # loads env + catalog
├── data/
│   ├── catalog.json            # D2 — invented Mumbai Marvels catalog
│   └── leads.csv               # provided leads (60 rows, 20 per segment)
├── core/
│   ├── __init__.py
│   ├── llm.py                  # Hugging Face Inference API wrapper + prompts
│   ├── sales_agent.py          # catalog Q&A + outreach generation (LLM + fallback)
│   └── lead_scorer.py          # D3 — scoring engine + stated data-quality rules
└── ui/
    ├── __init__.py
    ├── styles.py               # shared CSS / theme helpers
    ├── page_home.py            # hero, KPIs, how-it-works
    ├── page_catalog.py         # matches, prices, FAQ, offers, not-published
    ├── page_leads.py           # D3 — segment scoring + outreach generator
    └── page_chat.py            # AI sales chat with suggested questions
```

---

## D2 — Team catalog (invented)

`data/catalog.json` follows the structure of `catalog_template.json`:

- **Team:** Mumbai Marvels
- **Home venue:** Wankhede Stadium, Mumbai
- **4 matches** (IPL 2027): vs Delhi Dynamos, Chennai Chargers, Bengaluru Blasters, Kolkata Knights
- **4 seat areas:** North Stand (General), East Pavilion (Reserved), West Corporate Box, Family Enclosure
- **8 FAQ items:** child tickets, where to buy, payment methods, ID proof, group discount, entry timing, prohibited items, rain policy
- **3 things NOT published (with assumptions):** on-site parking, refund policy beyond rain, accessibility for wheelchair users
- **3 offers:** Early Bird 15% off, Student Pass 500 INR, Winback 20% off

The agent gives a safe, honest "please contact the box office" answer for the
not-published topics rather than inventing information.

---

## D3 — Lead scoring

We score the **winback** segment by default (you can switch to `new_buyer` or
`repeat_fan` in the UI). The model produces a 0-100 score from six signals:

| Signal           | Weight | What it captures |
|------------------|--------|------------------|
| Recency          | 20     | months since last purchase |
| Engagement       | 25     | email opens + sms replies + site visits |
| Intent           | 20     | cart abandons in 30d |
| Value            | 15     | lifetime tickets + avg spend |
| Contactability   | 10     | SMS/voice consent, DND status |
| Freshness        | 10     | days since last contact |

Tiers: **A-Hot ≥70**, **B-Warm ≥45**, **C-Cold <45**.

### Stated data-quality rules (no row is ever dropped)

- **R1** `tickets_bought_lifetime = -1` is impossible → set to 0 and flagged.
- **R2** blank `months_since_last_purchase` → kept as missing, flagged.
- **R3** blank `consent_sms`/`consent_voice` → treated as `N` (opt-in required), flagged.
- **R4** `dnd_registered = Y` → outreach channel restricted to email only.
- **R5** duplicate `name + city` pairs → both kept and flagged; dedupe happens at send time, not scoring time.
- **R6** `days_since_last_contact = 0` → valid ("contacted today").
- **R7** no row is dropped. Every flagged row is still scored and shown.

In the provided data this surfaces: `L037` (impossible `-1` lifetime tickets),
`L009`/`L032`/`L058` (blank consent), `L053` (missing purchase date), duplicate
name+city pairs (`L003`/`L004`, `L027`/`L028`, `L042`/`L044`), and several DND
leads whose channel is auto-restricted to email.

---

## The free LLM (Hugging Face)

This project uses the **Hugging Face Inference API** — free, easy, no credit card.

1. Create a free account at <https://huggingface.co>
2. Generate a **Read** token at <https://huggingface.co/settings/tokens>
3. Put it in `.env`:
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
   HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2
   ```

**No token? The app still works.** It falls back to a deterministic,
catalog-grounded rule engine so every feature stays functional. You will see a
yellow "rule-based fallback" status badge instead of the green "LLM" one.

Alternative free models you can set in `HF_MODEL`:
- `meta-llama/Meta-Llama-3-8B-Instruct`
- `HuggingFaceH4/zephyr-7b-beta`
- `mistralai/Mistral-7B-Instruct-v0.2`

---

## Step-by-step setup guide

### 1. Install Python
Python 3.9+ is required. Check:
```bash
python --version
```

### 2. Create a virtual environment (recommended)
```bash
cd ipl-ticket-agent
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 3. Install dependencies
Use the virtual environment's Python directly so the package is installed into the same environment that runs Streamlit:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you see `ModuleNotFoundError: No module named '_signal'` before the app starts, this is a broken Python installation or virtual environment, not an app error. Recreate the environment from the project folder:
```bash
rm -rf .venv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c "import _signal, signal, subprocess; print('Python runtime OK')"
.venv/bin/streamlit run app.py
```
On Windows, delete `.venv`, recreate it with `py -m venv .venv`, then use `.venv\\Scripts\\python.exe -m pip` and `.venv\\Scripts\\streamlit.exe`.

### 4. (Optional) add your free Hugging Face token
```bash
cp .env.example .env
# then edit .env and paste your HF_TOKEN
```
Skip this to run in rule-based fallback mode.

### 5. Run the app
```bash
streamlit run app.py
```
The browser opens at <http://localhost:8501>.

### 6. Use it
- **Home** — overview + engine status.
- **Catalog (D2)** — matches, prices, FAQ, offers, and the unpublished topics.
- **Lead Scoring (D3)** — pick a segment, see scored leads, view flags, generate outreach.
- **Sales Chat** — ask the AI agent about tickets, prices, kids, parking, refunds, offers.

---

## How the pieces fit together

```
data/catalog.json ──┐
                    ├─> core/sales_agent.py ──> ui/page_chat.py
                    │        ▲
                    │        └─ core/llm.py (Hugging Face + fallback)
                    │
data/leads.csv ─────┴─> core/lead_scorer.py ──> ui/page_leads.py
                                                (scoring + outreach)
config.py ── loads env + catalog, shared by all modules
app.py ── Streamlit entry, sidebar routing to ui/page_*.py
```

---

## Notes for the assignment

- Segment chosen for D3: **winback** (switchable in the UI).
- All scores and flags are shown in the table — transparency over magic.
- Outreach respects DND and consent: DND leads get "Email only"; missing
  consent defaults to `N`.
- The agent never invents prices/dates/policies; for unpublished topics it
  deflects to the box office.
- Every row in `leads.csv` is preserved — none dropped, all issues flagged.
