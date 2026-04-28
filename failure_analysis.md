# Universal Copilot Failure Analysis

Expanding from a narrow tool to a Universal Category Intelligence Layer introduces complex new failure modes. Here are the 5 major risks explicitly identified in our new architecture and how we mitigate them.

## 1. Overgeneralization
*   **Risk:** When queried with "Something for an active toddler", the multi-category router might pull candidates from 10 different categories (Toys, Gear, Feeding, Outdoor, etc.). If the LLM is fed 50 random products, it loses context and outputs a messy, generic recommendation array.
*   **Mitigation:** The Rule-layer is strictly capped. If a semantic cluster pulls too many items, we force the LLM to output a `clarifying_question` via the `uncertainty_note` field (e.g., "Active outdoors, or active at mealtime?") rather than guessing blindly.

## 2. Wrong Category Mapping
*   **Risk:** The phrase "bottle" maps to Feeding, but the user might have meant "water bottle holder" for a stroller. The AI recommends Dr. Brown's anti-colic bottles instead of stroller accessories.
*   **Mitigation:** The schema requires the LLM to output `relevant_categories`. The frontend exposes this (e.g., `Relevant Categories: Feeding`). If the mother sees the wrong category mapped, she immediately understands *why* the AI made the mistake, preserving trust.

## 3. Weak Cross-Category Reasoning
*   **Risk:** When given a multi-category query ("Traveling with toddler"), the AI successfully pulls a travel stroller and a travel cot, but its reasoning is completely disjointed, treating them as isolated purchases.
*   **Mitigation:** The system prompt explicitly commands the AI to output `why_recommended` specific to *her context* (the trip), forcing it to synthesize how the products work *together* on the flight.

## 4. Overconfidence
*   **Risk:** A mother asks "My baby has a severe fever and rash, what should I buy?". The AI confidently recommends a thermometer and fever cooling patches, assuming the role of a doctor.
*   **Mitigation:** The `detected_intent` field is designed to flag `troubleshooting`. Anti-hallucination rules strictly mandate that any health-related troubleshooting must prepend the `tradeoffs` or `avoid_if` fields with warnings to consult a pediatrician, preventing medical liability.

## 5. Missing Constraints (The "Basic Copilot" Flaw)
*   **Risk:** The user provides a strict budget (50 AED), but because no strollers exist under 50 AED, the AI silently drops the budget constraint and recommends a 1000 AED stroller.
*   **Mitigation:** We previously removed the "budget relaxation" fallback. If 0 products match the strict hard-constraints of the semantic router, the AI *must* halt and return a transparent error rather than inflating the budget.
