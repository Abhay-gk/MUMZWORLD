# Mumzworld Take-Home — Submission

## Track

**Track B** — Prototype

---

## One-Paragraph Summary

I built **Aisha**, a Universal AI Shopping Copilot for Mumzworld, designed for first-time mothers in the UAE who experience decision paralysis when choosing high-stakes baby gear. The core problem: a mother searching for a stroller sees 200+ results with identical marketing language ("lightweight," "safe," "premium") and no way to filter by the things that actually matter to her — whether it fits in her apartment elevator, whether it works for a newborn, or whether it stays under her real budget. Aisha replaces the search bar with a natural-language consultation: she accepts a plain-English description of the mother's situation, extracts hard constraints (budget, baby age, category) via a deterministic rule layer, routes across multiple product categories simultaneously, and passes a trimmed candidate set to a locally-run Phi-3 LLM which generates personalized, grounded recommendations — each one explicitly justifying *why it fits her life*, not generic product features. Every recommendation is anchored to real catalog products; the system has a structured fallback that guarantees no hallucinated products or blank error screens even when the LLM is unavailable. The prototype is a full-stack Flask application with a premium UI, running entirely on-device with zero cloud API cost.

---

## Prototype Access

**GitHub Repo:** [https://github.com/Abhay-gk/MUMZWORLD](https://github.com/Abhay-gk/MUMZWORLD)

**Run locally:**
```bash
# 1. Clone the repo
git clone https://github.com/Abhay-gk/MUMZWORLD.git
cd MUMZWORLD

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull the Phi-3 model (first time only, ~2GB)
ollama pull phi3

# 4. Start Ollama (keep running in a separate terminal)
ollama serve

# 5. Start the app
python app.py
# → Open http://localhost:5000
```

> Windows users: run `setup.bat` for a one-click startup.

---

## Markdown Deliverables

| File | Description |
|---|---|
| [`problem_definition.md`](problem_definition.md) | Discovery — persona, 3 grounded pain points, why this is high-leverage |
| [`ai_justification.md`](ai_justification.md) | Why AI — why traditional filters/UX cannot solve this, what AI capability is essential |
| [`show_your_work.md`](show_your_work.md) | Show Your Work — prompts that mattered, dead ends, lessons, cuts from scope |
| [`measurement.md`](measurement.md) | Measurement — leading indicator, 5% A/B test design, success/failure thresholds |
| [`EVALS.md`](EVALS.md) | 10-query evaluation across simple, multi-category, ambiguous, and adversarial cases |
| [`TRADEOFFS.md`](TRADEOFFS.md) | Explicit design decisions — what was cut, why, and what comes next |

---

## AI Usage Note

1. **Claude Sonnet (Antigravity IDE)** — Problem framing, system prompt engineering across 3 iterations, code generation for the Flask backend and rule-layer, UI scaffolding, and all documentation writing.
2. **Phi-3 (via Ollama, local)** — Runtime LLM for multi-constraint reasoning and personalized explanation generation; runs entirely on-device with no API cost.
3. **Mumzworld.com + Trustpilot** — Used manually (not AI) to ground the mock product catalog in real brands, UAE pricing, and authentic user pain points from reviews.
4. AI wrote the first draft of all `.md` files; I edited each for accuracy, added real product data by hand, and rewrote the system prompt three times based on observed phi3 failure modes.
5. The rule-based pre-filter, JSON extraction fallback strategies, and fallback scoring logic were co-designed with Claude but validated and debugged manually against phi3 outputs.

---

## Time Log

| Phase | Time |
|---|---|
| Discovery — browsing Mumzworld as Fatima, reading Trustpilot reviews, defining the problem | ~1 hr |
| Design — AI justification, solution architecture, system prompt v1 | ~1 hr |
| Build — `products.json` (30 real products), `app.py` (rule filter + Ollama client + fallback) | ~1.5 hr |
| UI — `index.html` (animated UI, constraint pills, 3-card results, loading states) | ~1 hr |
| Evaluation + iteration — 10 test queries, 3 system prompt rewrites, edge case hardening, docs | ~1 hr |
| **Total** | **~5.5 hrs** (slightly over — declared honestly) |
