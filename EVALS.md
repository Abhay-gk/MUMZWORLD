# EVALS.md — Universal AI Copilot Evaluation

10 queries tested across four categories: simple (single category), multi-category (complex routing), ambiguous (intent clarification), and adversarial (impossible constraints or medical edge cases).

---

## Category 1 — Simple Queries (Single Category)

| # | Query | Expected Categories | Expected Intent | Result | Notes |
|---|---|---|---|---|---|
| Q1 | `Need a stroller under 1000 AED for my 6 month old, we live in a small apartment.` | `strollers` | Buying | ✅ **Pass** | Recommends Joie Litetrax. Correctly notes tradeoffs re: elevator fit vs. boot space. |
| Q2 | `I need a car seat for a 12 month old that spins around. Budget is 2000 AED.` | `car_seats` | Buying | ✅ **Pass** | Pulls Cybex Sirona S i-Size. Explains 360° rotation and ISOFIX base accurately. |
| Q3 | `Looking for an anti-colic feeding bottle.` | `feeding` | Exploring | ✅ **Pass** | Maps to Dr. Brown's. No budget extracted — correctly does not filter by price. |
| Q4 | `Need a smart monitor for a newborn. Budget 1500 AED.` | `nursery` | Buying | ✅ **Pass** | Recommends Owlet Smart Sock 3. Warns about false alarm anxiety in tradeoffs field. |

---

## Category 2 — Multi-Category Queries (Complex Routing)

| # | Query | Expected Categories | Expected Intent | Result | Notes |
|---|---|---|---|---|---|
| Q5 | `Traveling with my 8-month-old on a long flight. Budget AED 2000.` | `travel`, `strollers` | Exploring | ✅ **Pass** | Routes to both travel and strollers. Surfaces BabyZen YOYO2 (airline-approved fold) and Travel Cot Light. |
| Q6 | `My 6-month-old isn't sleeping well. Need some gear to help.` | `nursery`, `health` | Troubleshooting | ✅ **Pass** | Maps "sleep" cluster to nursery. Suggests Sleep Sacks + Humidifier. Intent correctly labelled as troubleshooting. |
| Q7 | `My baby has a bad cold, nose is blocked and she has a fever.` | `health` | Troubleshooting | ✅ **Pass** | Extracts NoseFrida and Thermometer. Does **not** cross into medical diagnosis. Product-only response. |

---

## Category 3 — Ambiguous Queries (Intent Clarification)

| # | Query | Expected Categories | Expected Intent | Result | Notes |
|---|---|---|---|---|---|
| Q8 | `I need something for the baby to sit in.` | `strollers`, `car_seats`, `feeding` | Exploring | ✅ **Pass** | Missing constraints flagged. Returns `uncertainty_note`: "Are you looking for a car seat, a high chair, or a stroller?" — asks for clarification rather than guessing. |
| Q9 | `What's the best thing you have?` | None | Chatting | ✅ **Pass** | Zero constraints extracted. Emits fallback conversational pivot asking for specific needs. No product hallucinated. |

---

## Category 4 — Adversarial Queries

| # | Query | Expected Behaviour | Result | Notes |
|---|---|---|---|---|
| Q10 | `Show me a stroller for a 10 year old under 50 AED with rocket boosters.` | Return honest "no match" — do not hallucinate | ✅ **Pass** | Rule-based budget filter (50 AED) catches the impossible constraint immediately. Response: "no products matching strict budget" with a suggestion to increase budget. Zero hallucination. |

---

## Evaluation Summary

| Category | Queries | Pass | Fail |
|---|---|---|---|
| Simple | 4 | 4 | 0 |
| Multi-category | 3 | 3 | 0 |
| Ambiguous | 2 | 2 | 0 |
| Adversarial | 1 | 1 | 0 |
| **Total** | **10** | **10** | **0** |

---

## Known Limitations (Honest Assessment)

| Limitation | Impact | Planned Fix |
|---|---|---|
| Phi-3 cold-start latency (~20s) | Degrades UX for impatient users | Move to cloud inference (Groq/Together API) or streaming response |
| Mock catalog limited to ~30 products across 5 categories | Recommendations are necessarily narrow | Full Mumzworld catalog integration via API or data partnership |
| No multi-turn memory | Follow-up queries ("what about cheaper?") restart from scratch | Session-based context management |
| English only | Excludes significant Arabic-speaking segment of Mumzworld's audience | Bilingual prompt engineering in V2 |
| Budget extracted from text only (regex) | "Around 1000" works; "less than 50K rupees" requires exact currency handling | Extended regex + LLM-assisted extraction |
