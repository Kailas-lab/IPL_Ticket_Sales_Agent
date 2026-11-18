# Mumbai Marvels AI Ticket Sales Agent

## Live Demo

[🚀 View Live Project](https://iplticketapp.streamlit.app/)

## Client handoff guide

This project is a complete demonstration of an AI-assisted IPL ticket-sales workflow for the fictional **Mumbai Marvels** team.

It provides:

- A catalog-grounded fan question-and-answer assistant.
- Transparent lead scoring for sales prioritisation.
- Data-quality flags for imperfect lead data.
- Consent- and DND-aware outreach recommendations.
- Personalised outreach message drafts.
- A Streamlit web interface.
- Optional free Hugging Face LLM support with a working offline-style fallback.

All team, match, price, lead, and policy information is synthetic or assumed. It must not be treated as real Mumbai Marvels, IPL, stadium, or customer information.

---

## 1. What the client receives

### D2: Ticket catalog

The catalog is stored in `data/catalog.json` and is visible in the **Catalog (D2)** section of the app.

It contains:

- Team: Mumbai Marvels.
- Home venue: Wankhede Stadium, Mumbai.
- Four invented IPL 2027 home matches.
- Four seat areas with match-specific prices in INR.
- Eight frequently asked questions.
- Three offers.
- Three topics that are deliberately not published: parking, general refunds, and accessibility.

The assistant is designed not to invent information for unpublished topics. Instead, it gives a safe explanation and directs the fan to the box office where appropriate.

### D3: Lead scoring

The default scored segment is **winback**, meaning fans who purchased previously but have not purchased recently. The interface also allows `new_buyer` and `repeat_fan` to be selected.

The supplied file contains 60 synthetic leads:

| Segment | Number of leads |
|---|---:|
| new_buyer | 20 |
| winback | 20 |
| repeat_fan | 20 |
| Total | 60 |

The score is from 0 to 100:

| Signal | Weight | Purpose |
|---|---:|---|
| Recency | 20 | Time since the previous purchase |
| Engagement | 25 | Email opens, SMS replies, and site visits |
| Intent | 20 | Recent cart abandonment |
| Value | 15 | Lifetime purchases and average spend |
| Contactability | 10 | SMS/voice consent and DND status |
| Freshness | 10 | Time since the last contact |

Lead tiers:

- **A — Hot:** 70–100.
- **B — Warm:** 45–69.
- **C — Cold:** 0–44.

### Report summary

The scoring model is intentionally transparent rather than a black box. It helps a sales operator answer three questions:

1. Which leads show the strongest buying intent?
2. Which leads are valuable or engaged enough to prioritise?
3. Which contact channels are legally and operationally safe to use?

The supplied data is deliberately imperfect. The application keeps every row and displays quality flags rather than silently correcting or dropping data.

The following conditions are explicitly handled:

- `L037` has an impossible `tickets_bought_lifetime` value of `-1`. It is scored using a cleaned value of `0` and remains flagged.
- `L053` has a missing `months_since_last_purchase` value. It remains in the output and is flagged as unknown.
- Blank SMS or voice consent values are conservatively treated as `N` and flagged.
- Duplicate name-and-city pairs are kept and flagged. Deduplication should happen before sending a campaign, not during scoring.
- Leads with `dnd_registered = Y` receive an **Email only (DND)** channel recommendation.
- `days_since_last_contact = 0` is treated as a valid “contacted today” value.
- No lead is silently removed.

The full scoring rules are available inside the **Lead Scoring (D3)** page and in `core/lead_scorer.py`.

---

## 2. Project folder structure

```text
ipl-ticket-agent/
├── app.py                      Streamlit entry point
├── config.py                   Application configuration and catalog loading
├── requirements.txt            Python dependencies
├── .env.example                Optional Hugging Face configuration template
├── README.md                   This client handoff guide
├── data/
│   ├── catalog.json            D2 invented team catalog
│   ├── leads.csv               60-row synthetic lead file
│   └── test_set.json           Catalog and lead-scoring acceptance tests
├── core/
│   ├── __init__.py
│   ├── llm.py                  Hugging Face API wrapper and catalog context
│   ├── sales_agent.py          Fan Q&A and outreach generation
│   └── lead_scorer.py          Lead scoring and data-quality rules
└── ui/
    ├── __init__.py
    ├── styles.py               Shared visual styling
    ├── page_home.py            Overview page
    ├── page_catalog.py         Catalog page
    ├── page_leads.py           Lead scoring page
    └── page_chat.py            Sales chat page
```

---

## 3. Client setup instructions

### Step 1: Install Python

Install Python 3.9 or newer. Check the installation with:

```bash
python --version
```

On some systems, use `python3` instead of `python`.

### Step 2: Open the project folder

From the folder containing this README:

```bash
cd ipl-ticket-agent
```

### Step 3: Create a virtual environment

macOS and Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 4: Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The required packages are:

- Streamlit for the web interface.
- Pandas for reading and scoring leads.
- Requests for the Hugging Face API call.
- Python-dotenv for optional local configuration.

### Step 5: Start the application

```bash
streamlit run app.py
```

Streamlit will show a local address in the terminal and normally opens the app in a browser automatically.

### Step 6: Use the application

1. Open **Home** to confirm the application status.
2. Open **Catalog (D2)** to review matches, prices, FAQs, offers, and unpublished topics.
3. Open **Lead Scoring (D3)** to select a segment and review the prioritised leads.
4. Select a lead to create an outreach draft.
5. Open **Sales Chat** to ask catalog questions.

### If the `_signal` error appears

If startup fails with `ModuleNotFoundError: No module named '_signal'`, Python is failing before the application loads. This means the virtual environment or Python installation is damaged.

Recreate the environment from inside `ipl-ticket-agent`:

```bash
rm -rf .venv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c "import _signal, signal, subprocess; print('Python runtime OK')"
.venv/bin/streamlit run app.py
```

On Windows, delete the `.venv` folder, recreate it with `py -m venv .venv`, and use `.venv\Scripts\python.exe` and `.venv\Scripts\streamlit.exe`.

---

## 4. Optional Hugging Face AI setup

The app works without an API key using its catalog-grounded rule-based fallback.

To enable free Hugging Face text generation:

1. Create a Hugging Face account.
2. Create a free read-only access token.
3. Copy `.env.example` to `.env`.
4. Add the token to `.env`:

```text
HF_TOKEN=your_token_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

Do not commit `.env` or share the token. The provided `.gitignore` should be used to keep secrets out of the project.

When the token is available, the Home page and Sales Chat page show the Hugging Face model status. If the model cannot be reached or is warming up, the app automatically returns to the fallback behaviour.

---

## 5. Test set and acceptance checks

The reusable test set is in `data/test_set.json`.

### Catalog test set

The test set checks that the assistant can answer:

- Home-match schedule questions.
- Match and seat-area pricing questions.
- Child-ticket questions.
- Student-offer questions.
- Parking questions.
- Refund questions.
- Accessibility questions.
- Early-bird offer questions.

For the three unpublished topics, the expected result is an honest limitation and a box-office direction. The assistant should not create an unsupported policy.

### Lead-scoring test set

The test set checks that:

- The selected segment displays 20 leads.
- No rows are silently dropped.
- L037 is flagged for the impossible negative lifetime-ticket value.
- L053 is flagged for a missing purchase-recency value.
- Blank consent is treated conservatively.
- DND leads are limited to email recommendations.
- Outreach can be generated for a selected lead.

### Suggested manual test procedure

1. Start the app.
2. Open **Sales Chat**.
3. Ask each question in `data/test_set.json` under `catalog_questions`.
4. Compare the answer with the expected behaviour in that file.
5. Open **Lead Scoring (D3)**.
6. Select `winback`.
7. Confirm that 20 leads appear.
8. Inspect the rows and flags listed under `lead_scoring_checks`.
9. Select a lead and generate an outreach message.

---

## 6. Demo video

Demo video link: **To be added by the project owner**

Recommended demonstration sequence:

1. Show the Home page and engine status.
2. Open the catalog and show matches, prices, offers, and unpublished topics.
3. Ask the Sales Chat about ticket prices and a deliberately unpublished topic such as parking.
4. Open Lead Scoring and select the winback segment.
5. Show the score tiers and data-quality flags.
6. Select a lead and generate a personalised outreach message.
7. Show that DND leads are restricted to email.

The video should clearly state that all data is synthetic and that the team and catalog are invented for the caselet.

---

## 7. AI tools used and where

### Hugging Face Inference API

Used in:

- `core/llm.py`: sends catalog-grounded prompts to the selected Hugging Face text-generation model.
- `core/sales_agent.py`: uses the generated result for fan answers and outreach drafts when the API is available.
- `ui/page_chat.py`: displays the AI chat experience and the active engine status.
- `ui/page_leads.py`: uses the model to create personalised outreach drafts when available.

The model receives only the catalog context and the selected lead details required to draft the response. It is instructed not to invent prices, dates, or policies.

### Rule-based fallback

Used in:

- `core/sales_agent.py`: answers common catalog questions when no Hugging Face token is configured or the model is unavailable.

This fallback is not a second AI model. It is deterministic application logic that keeps the demonstration usable without an external model.

### AI-assisted development disclosure

AI assistance was used to help structure the application, write the Streamlit interface, create the catalog assumptions, document the scoring rules, and prepare the test cases. The final application logic, catalog content, scoring assumptions, and safety rules should be reviewed by the client before production use.

---

## 8. Important production limitations

This is a caselet demonstration, not a production ticketing system.

Before production use, the client should add:

- A real ticket inventory and booking system.
- A verified payment provider.
- Authenticated staff access.
- A consent and suppression-list service.
- Audit logs for campaign decisions.
- Human approval before sending outreach.
- Real accessibility, parking, refund, and stadium policies.
- Monitoring and rate limits for the external AI service.
- Formal legal and privacy review.

Never use the supplied synthetic leads to contact real people.

---

## 9. Quick reference

| Item | Location |
|---|---|
| Start the app | `streamlit run app.py` |
| Catalog | `data/catalog.json` |
| Synthetic leads | `data/leads.csv` |
| Acceptance test set | `data/test_set.json` |
| Scoring rules | `core/lead_scorer.py` |
| AI API wrapper | `core/llm.py` |
| Fan Q&A and outreach | `core/sales_agent.py` |
| Main UI | `app.py` |
