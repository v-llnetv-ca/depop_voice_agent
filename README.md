# Depop Voice Support Agent

A voice-first AI support triage agent built for Depop, demonstrating how ElevenLabs' speech synthesis and Claude's reasoning capabilities can be deployed against a real operational problem in a high-volume consumer marketplace.

---

## The Problem

Depop carries a 1.3-star Trustpilot rating across 7,000+ reviews. The overwhelming majority of complaints are not complex — they are the same six support queries asked by different people every day: item not received, item not as described, authenticity disputes, payout delays, account suspensions, and fee confusion.

Depop has no live chat. Users submit tickets and wait days for a first response — often missing the 30-day dispute window while they do. The problem isn't knowledge or policy. It's delivery.

→ Full discovery brief in [`docs/discovery-brief.md`](docs/discovery-brief.md)

---

## The Solution

A voice support triage agent that:

- Accepts user input by **voice or text**
- **Classifies** the issue into one of eight support categories using Claude
- **Retrieves** the relevant policy from a structured knowledge base
- **Decides** whether to resolve directly or escalate to human support
- **Responds** in natural, human-sounding speech via ElevenLabs TTS (River voice)
- If escalating, surfaces a structured handoff so the human agent has full context

The agent handles the repetitive 60%. Human agents handle the complex 40% — with better context and less backlog.

---

## Architecture

![System Architecture](docs/system_architecture.png)

**User layer** — voice input via Web Speech API or text fallback → web frontend

**Agent backend** — Flask API → Claude (classification + decision reasoning) → knowledge base JSON → ElevenLabs TTS

**Decision logic** — after classification, the agent checks escalation triggers before responding. Authenticity claims, fraud cases, and ambiguous multi-category queries always escalate. Everything else resolves directly.

---

## Demo

Watch the demo on Loom: (https://www.loom.com/share/2732ddf4d962414fa539720f801b291f) 

Four scenarios demonstrating the full decision range:

| Scenario | Input | Outcome |
|---|---|---|
| 1 | Item not shipped after 5 days | Resolves with policy guidance |
| 2 | Suspected counterfeit item | Escalates — always escalates flag |
| 3 | Ambiguous buyer/seller dispute | Asks clarifying question, then resolves |
| 4 | Multi-category query | Deliberate failure — escalates gracefully |

---

## Tech Stack

- **Python** / Flask — backend and agent logic
- **Anthropic Claude API** — issue classification and resolution reasoning
- **ElevenLabs API** — text to speech (River voice)
- **Web Speech API** — browser-native voice input
- **p5.js** — animated voice button
- **HTML / CSS / JS** — single-file frontend, no framework

---

## Project Structure

```
depop-voice-agent/
├── backend/
│   ├── app.py              # Flask server, API endpoints
│   ├── agent.py            # Classification, policy lookup, decision logic, TTS
│   └── knowledge_base.json # Structured Depop policy data (8 categories)
├── frontend/
│   └── index.html          # Single-file UI — voice input, reasoning display, response
├── demo/
│   └── scenarios.md        # Test scenarios with expected inputs and outputs
├── docs/
│   ├── discovery-brief.md  # Customer problem, evidence base, commercial case
│   ├── architecture.png    # System architecture diagram
│   └── deployment-considerations.md
├── .env.example
├── requirements.txt
└── README.md
```

---

## Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/depop-voice-agent.git
cd depop-voice-agent
```

**2. Create a virtual environment and install dependencies**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Set up environment variables**
```bash
cp .env.example .env
```
Add your API keys to `.env`:
```
ANTHROPIC_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
```

**4. Run the app**
```bash
python backend/app.py
```

**5. Open in Chrome**

Go to `http://127.0.0.1:5000`

Voice input requires Chrome. Text input works in any browser.

---

## Agent Decision Logic

```
User message
    ↓
Classification (Claude) → one of 8 categories
    ↓
Policy lookup → knowledge_base.json entry
    ↓
Escalation check → always_escalates flag or ambiguous category?
    ↓
    ├── Yes → generate escalation response + handoff guidance
    └── No  → clarification needed?
                ├── Yes → ask one clarifying question
                └── No  → generate resolution response
                              ↓
                         ElevenLabs TTS → spoken response
```

---

## Knowledge Base Categories

| Category | Escalates | Description |
|---|---|---|
| `shipping_dispute` | Sometimes | Item not received, tracking issues |
| `item_not_as_described` | Sometimes | Wrong item, undisclosed damage |
| `authenticity_claim` | Always | Counterfeit or fake item |
| `refund_request` | Sometimes | Refund and return requests |
| `payout_delay` | Sometimes | Seller hasn't received payment |
| `payment_and_fees` | Rarely | Unrecognised charges, balance queries |
| `fraud_and_safety` | Always | Scams, off-platform payments, suspicious activity |
| `ambiguous` | Always | Multi-category or unclear queries |

---

## What a Production Deployment Would Require

This is a working prototype. Moving to production would require:

- **Zendesk integration** — logging agent interactions and routing escalations into Depop's existing ticketing system
- **Authentication layer** — verifying user identity before discussing order-specific details
- **Live knowledge base pipeline** — connecting to Depop's help centre so policy updates propagate automatically without manual JSON editing
- **Legal review** — any AI-generated support responses need review for liability exposure in consumer protection contexts
- **GDPR compliance** — voice data handling, storage, and retention policy
- **Phased rollout** — pilot on one query type (e.g. non-delivery only) before expanding, with A/B testing against current support flow

---

## About This Project

Built by **Vullnet Voca** as a portfolio demonstration of applied voice AI deployment strategy.

Background: 6+ years across market and user research, enterprise product discovery, and applied AI product development. MSc Data Science & AI (Distinction), UAL Creative Computing Institute.

[LinkedIn](https://www.linkedin.com/in/vullnetvoca/) · [GitHub](https://github.com/v-llnetv-ca)
