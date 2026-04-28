# 3. System Design

## End-to-End Flow

1. **Input:** User submits a natural language query (e.g., "Need a stroller under 1000 AED for my 6 month old, we live in a small apartment").
2. **Rule-Based Parsing:** The backend uses Regex to extract hard constraints (`budget_max=1000`, `baby_age_months=6`, `category=stroller`).
3. **Pre-Filtering (Rules):** The backend filters the local catalog JSON against the hard constraints. This reduces the candidate pool from the full catalog down to a maximum of 10-15 valid, in-stock products.
4. **Prompt Construction:** The backend injects the user's raw query and the JSON subset of candidate products into a strict prompt template optimized for the Phi-3 model.
5. **AI Inference:** The local Ollama instance (Phi-3) evaluates the candidates against the implicit/semantic needs (e.g., "small apartment") and generates a structured JSON response with the top 3 picks, reasoning, and tradeoffs.
6. **Validation:** The backend validates that the response is strictly formatted JSON and that all required fields (like `confidence_score` and `avoid_if`) are present. If data is insufficient, an empty array is returned.
7. **Output:** The frontend receives the structured payload and renders personalized recommendation cards to the user.

## Clear Separation: AI vs. Rule-Based Logic

| Responsibility | Rule-Based Layer (Python) | AI Layer (Phi-3 via Ollama) |
| :--- | :--- | :--- |
| **Parsing numbers/categories** | ✅ Extracts Budget and Age limits | ❌ |
| **Filtering hard constraints** | ✅ Drops products > budget or out-of-stock | ❌ |
| **Evaluating qualitative needs** | ❌ | ✅ Matches "apartment" to "compact fold" |
| **Ranking** | ❌ | ✅ Weighs pros/cons to pick the Top 3 |
| **Generating explanations** | ❌ | ✅ Writes personalized `why_recommended` |
| **Handling edge cases** | ✅ Fallback logic if LLM fails | ✅ Recognizes contradictory/impossible queries |

## Minimal Architecture Diagram

```text
[ User Interface ]  -- "Stroller for newborn, 800 AED, flat" -->  [ Flask Backend ]
                                                                        |
                                                                  (Extract Rules)
                                                                        |
                                                          [ Rule-Based Pre-Filter ]
                                                          (Drops items > 800 AED)
                                                                        |
                                                               (Candidate JSON)
                                                                        |
                                                             [ Prompt Builder ]
                                                                        |
                                                               (System + User Prompt)
                                                                        |
                                                     [ Local Ollama Engine (Phi-3) ]
                                                                        |
                                                           (Strict JSON Response)
                                                                        |
                                                           [ Validation Layer ]
                                                                        |
[ Render 3 Product Cards ] <--- (Validated JSON payload) -------------- |
```
