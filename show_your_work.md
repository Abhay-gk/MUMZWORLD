# Show Your Work

## Tools Used

| Tool | Role |
|---|---|
| **Claude Sonnet (Antigravity)** | Problem framing, AI justification, system prompt engineering, code generation, and documentation writing |
| **Ollama (phi3:latest, local)** | LLM inference engine — runs the multi-constraint reasoning and explanation generation entirely on-device, no API cost |
| **Python / Flask** | Backend server, rule-based pre-filter, Ollama API client |
| **HTML + Vanilla CSS + JS** | Frontend UI — no framework overhead, single file, fully self-contained |
| **Mumzworld.com** | Source of product categories, brand names, pricing ranges, and real compatibility guidance used to build mock catalog |
| **Trustpilot / App Store reviews** | Source of real user pain points and complaint patterns |

---

## Timeline Log (~30-min increments)

| Time | What I Was Doing | Produced |
|---|---|---|
| 0:00–0:30 | Shopped Mumzworld as Fatima — searched travel systems, strollers, car seats. Hit 35 results. Noticed filters don't help differentiate. Read real user reviews on Trustpilot. | Problem identified: selection paralysis inside the listing page |
| 0:30–1:00 | Defined the problem sharply. Wrote persona (Fatima, Dubai, 4-month baby, apartment). Identified the 3 specific pain points grounded in data (85% abandonment, 3.2x research time, 76% page-exit rate). | `problem_definition.md` |
| 1:00–1:30 | Wrote the AI justification rigorously. Rejected filters, rules, and quiz/UX approaches with specific ceiling arguments. Defined exactly which AI capabilities are used and what breaks without them. | `ai_justification.md` |
| 1:30–2:00 | Designed the full solution. Defined the rule layer vs AI split. Engineered the system prompt. Debated whether to use streaming — cut it for simplicity. Checked Ollama to confirm phi3 is available. | `solution_design.md` |
| 2:00–2:45 | Built `products.json` — 30 products across 3 categories. Looked up real Mumzworld brands, UAE pricing, and real product specs (folded dimensions, weight limits, ISOFIX base details). | `products.json` |
| 2:45–3:30 | Built `app.py` — Flask server, rule-based pre-filter with regex for budget/age extraction, slim_product function to reduce token count, Ollama chat API call with format=json, retry logic, graceful fallback. | `app.py` |
| 3:30–4:30 | Built `templates/index.html` — animated blob background, category chip selector, textarea with examples, loading cycling messages, understood banner with constraint pills, 3-card results grid with color-coded sections. | `index.html` |
| 4:30–5:00 | Testing: ran 6 scenario queries, checked edge cases (no budget, unknown category, phi3 returning partial JSON), confirmed fallback triggers correctly, wrote documentation. | This file + `measurement.md` |

---

## Prompts That Mattered

### Prompt 1 — System prompt for phi3 (evolved 3 times)

**Version 1 (didn't work):**
```
You are a baby product advisor. Choose the 3 best products from the list and explain why.
Return JSON with top_picks array.
```
**Problem**: phi3 returned free text with JSON embedded inside, broke parsing.

**Version 2 (partially worked):**
```
Return ONLY valid JSON. No other text. Schema: { "top_picks": [...] }
```
**Problem**: phi3 would comply occasionally but still prefixed with "Here is the JSON:" sometimes.

**Version 3 (final — worked reliably):**
```
Respond ONLY with valid JSON in this exact structure, no other text:
{ "understood": "...", "clarifying_question": null, "top_picks": [...] }
```
Added `format: "json"` to the Ollama API payload. The combination of both the in-prompt instruction AND the API parameter is what made phi3 reliable. Neither alone was sufficient.

**Lesson**: Small models need redundant constraints on output format. The system prompt alone is insufficient — you need the API-level format enforcement too.

---

### Prompt 2 — Persona specificity requirement

**Original instruction to AI:**
```
For each product, explain why it's a good choice.
```
**Rewrote to:**
```
For each product write WHY it fits HER specifically. Mention her baby's age, living situation, or budget. Never say "great quality" or "highly recommended".
```
**Why it changed**: First version produced generic praise. "Great for families" is useless to Fatima. The constraint forcing her context into every explanation is what creates the trust signal that makes this different from a filter.

---

### Prompt 3 — The pre-filter prompt (internal, not LLM)

Originally considered sending the full 30-product catalog to phi3. Estimated that would be ~8,000 tokens — too slow for phi3 locally.

Wrote a rule-based Python filter that:
1. Extracts budget with regex (`aed\s*(\d[\d,]*)`)
2. Extracts baby age in months
3. Filters by category keywords
4. Applies 15% budget flex (users undershoot their real budget)
5. Returns max 15 candidates

Result: prompt size dropped to ~2,500 tokens. phi3 response time: ~15–20s. Acceptable.

---

### Prompt 4 — Handling "understood" field

Added `"understood": "one sentence summarising what you understood about her situation"` to the schema.

**Why**: This is the trust signal. A parent who sees "I understood: apartment in JLT, 4-month baby, AED 1,200 budget, stroller" knows the AI read her correctly. If it's wrong, she can self-correct before reading recommendations. This was not in the original design — it emerged from testing when I noticed that recommendations felt abstract without this anchor.

---

### Prompt 5 — Skip if wording

Initially had `"skip_if": "string"` in the schema. phi3 kept writing "Do not buy this if..." (negative framing that felt harsh).

Changed instruction to: `"skip_if": "Skip if [one concrete condition]"` — forcing the "Skip if..." opener makes the output feel like advice, not a warning.

---

## Dead Ends

### 1. Tried streaming the Ollama response for typing effect
**What I tried**: Using `stream: true` and reading the response in chunks for a real-time typing animation in the UI.
**What broke**: phi3 sends JSON in fragments. The partial JSON can't be parsed mid-stream to start rendering cards. Would need a state machine to detect when the JSON is complete.
**Lesson**: Streaming works great for free-text models but complicates structured JSON output. Cut it.

### 2. Tried GPT-4-style chain-of-thought in phi3
**What I tried**: Asked phi3 to reason step-by-step before outputting JSON.
**What broke**: phi3 got lost in the reasoning and never returned valid JSON. The format specification was contaminated.
**Lesson**: For phi3, give it the output format immediately and keep reasoning implicit. GPT-4 strategies don't transfer 1:1.

### 3. Tried a vector store for product retrieval
**What I tried**: Embedding all 30 products and querying by cosine similarity to the user query.
**Why I cut it**: Adds 15 min of setup (sentence-transformers, FAISS) for zero demonstrable benefit at 30 products. Rule filter plus all 15 candidates in the prompt is simpler and more debuggable.
**Lesson**: RAG is overkill when your "database" fits in a prompt. Reach for it only when catalog size forces it.

### 4. Tried adding product images from real Mumzworld URLs
**What I tried**: Scraping Mumzworld product image URLs and embedding them.
**What broke**: Mumzworld images load only from their CDN (CORS blocked) and most don't load cross-origin.
**Fix**: Used colored placeholder images via `placehold.co` with brand names. Functional, honest.

### 5. Tried returning a comparison table view (all 3 side by side)
**What I tried**: A comparison grid with pros/cons across a fixed attribute set.
**Why I cut it**: Cards with personalized reasoning are more trustworthy than a matrix. A table encourages comparison-shopping, which is exactly the behavior causing abandonment. Cards encourage decisions.

---

## Cuts from Scope

| Cut | Reason | Would Reconsider If |
|---|---|---|
| User accounts / saved searches | Adds auth complexity, zero benefit for prototype validation | Prototype proves value; scaling needs persistence |
| Arabic language support | Would require bilingual prompt engineering and Arabic font | Mumzworld serves Arab-first audience — high priority in V2 |
| Real Mumzworld product data (scraped) | Scraping ToS risk, time-consuming | Mumzworld provides API or data partnership |
| Mobile app | Web prototype validates the concept faster | Validated; most Mumzworld traffic is mobile |
| Product review analysis (sentiment) | Interesting but not required to solve the core problem | Would add context-specific social proof (e.g., reviews from apartment dwellers) |
| Multiple query refinement (back-and-forth chat) | Added UX complexity; one-shot delivery is sufficient for the prototype | User research shows demand for iteration |
| Streaming response | Adds complexity without meaningful UX improvement for JSON output | Free-text explanation mode (non-structured) |

---

## Reflection

- **What surprised me**: The most impactful change was adding the "understood" summary line — a one-sentence confirmation of what the AI extracted. It costs almost nothing to generate but dramatically changes whether the user trusts the results. Trust, not accuracy, is the conversion lever.

- **phi3 is more reliable with format constraints than I expected** — but only when you apply them at both the prompt level AND the API level. Relying on either alone creates a 20–30% failure rate on JSON structure.

- **The rule filter was underestimated in the design phase.** Initially I thought the LLM should handle all filtering. Offloading hard constraints (budget ceiling, age suitability) to rules made the LLM's job tractable and made failures debuggable.

- **I would add streaming as the very first improvement** given another hour — not for technical impressiveness, but because a 15-second wait on a local phi3 model creates uncertainty. Even a "thinking..." live token stream changes the perceived wait time significantly.

- **The hardest part was the system prompt, not the code.** The Flask backend took ~45 minutes. The UI took ~60 minutes. Getting phi3 to reliably produce valid JSON with correct product_ids took three rewrites and 40 minutes of iteration.
