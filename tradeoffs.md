# TRADEOFFS.md — Design Decisions and Explicit Cuts

This document records every significant engineering and product decision made during the 5-hour build, with explicit reasoning for each choice.

---

## Architecture Decisions

### Decision 1 — Local LLM (Phi-3 via Ollama) over Cloud API

**Chose**: Phi-3:latest running locally via Ollama  
**Rejected**: OpenAI GPT-4o, Anthropic Claude (cloud APIs)

**Why**: Zero API cost. No internet dependency. No data privacy concerns (mothers' queries about sick babies never leave the device). Demonstrates that an AI advisor of this quality can run on consumer hardware — a genuine cost argument for a startup like Mumzworld that wants to pilot before committing to cloud LLM spend.

**Real cost**: phi3 cold-start latency of ~15–20 seconds is noticeable. GPT-4o would be 2–3 seconds. This is the primary tradeoff accepted.

---

### Decision 2 — Rule-Based Pre-Filter before LLM (Hybrid Architecture)

**Chose**: Extract budget/age with regex first, filter the catalog, then send ≤15 candidates to the LLM  
**Rejected**: Sending the full catalog to the LLM for every query

**Why**:  
- Full 30-product catalog = ~8,000 tokens. phi3 degrades significantly on long contexts.  
- Hard constraints (budget ceiling, age suitability, in-stock status) should never be "reasoned about" — they should be enforced. The LLM's job is qualitative matching, not arithmetic.  
- When the LLM fails (timeout, bad JSON), the rule layer still has valid candidates and can generate a personalised fallback without showing an error.

**Real cost**: The regex budget extractor has known failure modes (free-text numbers like "around a thousand"). Mitigated by using 15% budget flex and catching edge cases.

---

### Decision 3 — Strict JSON Schema Enforcement (Dual Constraint: Prompt + API)

**Chose**: Enforce JSON output via both the system prompt instruction AND `format: "json"` in the Ollama API payload  
**Rejected**: Free-text response with post-hoc JSON extraction only

**Why**: phi3 has a ~20–30% failure rate on JSON compliance if only the prompt instructs it. The API-level format parameter brings this to near-zero. Both constraints together are required — neither alone is sufficient.

**Real cost**: JSON-only mode prevents streaming (chunked JSON is unparseable mid-stream). Accepted for reliability over UX polish.

---

## Explicit Cuts (What Was NOT Built)

### Cut 1 — No Database or Vector Store

**What was skipped**: PostgreSQL, Elasticsearch, or Pinecone for product storage  
**What was used instead**: Flat `products.json` loaded into memory at server startup

**Why cut**: Adds infrastructure overhead (Docker, connection strings, migrations) with zero demonstrable benefit for a 30-item mock catalog. A vector store only earns its complexity when the catalog exceeds ~500 items and keyword matching breaks down semantically. At 30 items, a well-written rule filter is faster, more debuggable, and more reliable.

**Would reconsider when**: Catalog scales to 10,000+ SKUs; replace the keyword filter with FAISS or Pinecone semantic search.

---

### Cut 2 — No Multi-Turn Conversational Memory

**What was skipped**: Session state, follow-up query handling ("what about a cheaper one?")  
**What was built instead**: One-shot query → response

**Why cut**: Multi-turn requires session management, growing context windows, and handling anaphora ("that one" → which product?). phi3 degrades with long conversation history. A highly accurate one-shot answer outperforms a broken or confused multi-turn chat. The `uncertainty_note` field asks for clarification in a single pass.

**Would reconsider when**: Switching to a model with stronger multi-turn coherence (GPT-4o, Claude) and implementing session persistence.

---

### Cut 3 — No Streaming Response

**What was skipped**: Server-Sent Events (SSE) for real-time token-by-token display  
**Why cut**: phi3 sends JSON in fragments. Partial JSON cannot be rendered as product cards mid-stream without a complex state machine. The 20-second wait is mitigated by rotating "thinking..." messages in the UI.

**Would reconsider when**: Switching to a free-text explanation mode (non-structured) where partial content renders naturally.

---

### Cut 4 — No Real Mumzworld Product Data

**What was skipped**: Scraping live Mumzworld SKUs, prices, and images  
**Why cut**: Scraping ToS risk. Image CDN is CORS-blocked. Building a scraper would take 2+ hours for fragile benefit.

**What was used instead**: 30 hand-curated products based on real Mumzworld brands (Joie, Cybex, BabyZen, Owlet), UAE market pricing verified manually, and real product specs.

**Would reconsider when**: Mumzworld provides a data API or a partnership for catalog access.

---

### Cut 5 — No Arabic Language Support

**What was skipped**: Bilingual prompting, Arabic font rendering, RTL layout  
**Why cut**: Bilingual system prompt engineering doubles prompt complexity. Arabic text rendering in a time-constrained prototype is a distraction from the core AI reasoning challenge.

**Why it matters**: Mumzworld's primary audience is Arab-speaking mothers. This is a high-priority V2 item, not a deprioritised one.

---

### Cut 6 — No User Accounts or History

**What was skipped**: Auth, saved searches, past recommendations  
**Why cut**: Adds auth infrastructure complexity. The prototype validates the core value proposition — the right product, with the right explanation, for this mother's specific situation — before persistence is warranted.

---

## What Would Be Built Next (Given +5 Hours)

| Priority | Feature | Business Reason |
|---|---|---|
| 1 | Cloud LLM inference (Groq/Together API) | Reduces latency from ~20s to ~2s — critical for mobile UX |
| 2 | Streaming response (SSE) | Eliminates perceived wait; even 5 tokens/second feels instant |
| 3 | Follow-up clarification UX | "I need a stroller" → dynamic form: "What's your budget?" / "Any elevator?" |
| 4 | Arabic language support | Serve Mumzworld's primary demographic |
| 5 | Full Mumzworld catalog integration | Real SKUs, real prices, real images, real stock status |
