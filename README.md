# Aisha — Universal AI Shopping Copilot for Mumzworld

## What I Built

**Aisha** is an AI-powered shopping advisor for Mumzworld that replaces the traditional search bar with a natural-language consultation experience. Built for first-time mothers in the UAE who face decision paralysis when choosing high-stakes baby gear (strollers, car seats, feeding equipment), Aisha accepts messy, real-world inputs like *"My 6-month-old isn't sleeping. We live in a small apartment, budget around 1000 AED"* — extracts hard constraints via a rule-based layer, routes them across multiple product categories, and passes a trimmed candidate set to a local Phi-3 LLM (via Ollama) which generates personalized, grounded recommendations with explicit tradeoffs. Every recommendation is anchored to the mother's specific situation; nothing is hallucinated — if no product fits, the system says so honestly. The result is a full-stack prototype (Flask + Vanilla HTML/CSS/JS) that transforms Mumzworld from a catalog into a trusted shopping consultant.

---

## Track

**Track B** — Live prototype (run locally with instructions below)

---

## Setup Instructions

### Prerequisites

| Dependency | Version | Install |
|---|---|---|
| Python | 3.9+ | [python.org](https://python.org) |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| Phi-3 model | phi3:latest | `ollama pull phi3` |

### Steps

```bash
# 1. Clone / download the project
cd MUMZWORLD

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Pull the Phi-3 model (first time only, ~2GB download)
ollama pull phi3

# 4. Start Ollama in a terminal (keep it running)
ollama serve

# 5. In a second terminal, start the Flask app
python app.py

# 6. Open your browser
# → http://localhost:5000
```

> **Windows one-click**: Run `setup.bat` — it starts Ollama and the Flask server together.

### Expected behaviour

- Ollama must be running at `http://localhost:11434` (default port)
- First query takes ~15–25 seconds (phi3 cold start); subsequent queries are faster
- If Ollama is unavailable, the app automatically falls back to rule-based recommendations — you will **never** see a blank screen or error page

---

## Project Structure

```
MUMZWORLD/
├── app.py                  # Flask backend — rule filter + Ollama client + routes
├── products.json           # 30-product mock catalog (real brands, UAE pricing)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Full UI — single file, Vanilla HTML/CSS/JS
├── static/                 # Static assets
│
├── README.md               # ← You are here
├── SUBMISSION.md           # Summary paragraph + AI note + time log
├── EVALS.md                # 10-query evaluation table
├── TRADEOFFS.md            # Design decisions and explicit cuts
│
├── problem_definition.md   # Discovery: persona, pain points
├── ai_justification.md     # Why AI (not filters or rules)
├── solution_design.md      # Architecture and rule/AI split
├── show_your_work.md       # Prompts, dead ends, lessons learned
└── measurement.md          # Success metrics and A/B test design
```

---

## Demo Queries to Try

| Query | What it tests |
|---|---|
| `My 6-month-old isn't sleeping well. We live in a small apartment. Budget 1000 AED.` | Multi-category routing (nursery + health), ambiguous intent |
| `Need a stroller under 800 AED for my 4-month-old, 5th floor walkup, no elevator.` | Hard constraint filtering + apartment-specific reasoning |
| `Traveling with my 8-month-old on a long flight. Budget AED 2000.` | Cross-category (travel + strollers + car seats) |
| `My baby has a blocked nose and a fever.` | Medical safety guardrail — no product hallucination |
| `Show me a stroller for a 10-year-old under 50 AED with rocket boosters.` | Adversarial/impossible constraint handling |
