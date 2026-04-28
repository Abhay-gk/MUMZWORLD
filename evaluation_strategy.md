# AI Evaluation Strategy

## 1. Test Cases

### Normal Cases (5)
1. **Active Mom:** "I need a stroller for jogging and outdoor walks. My baby is 6 months old." (Target: Jogging strollers, rugged wheels)
2. **Apartment Dweller:** "I live in a high-rise apartment in Dubai with a small elevator. Need a stroller for a newborn." (Target: Compact, suitable_for_apartment, flat recline)
3. **Budget-Conscious:** "Looking for an infant car seat under 500 AED. Baby is due next month." (Target: Juniors Mixfix G or similar)
4. **Frequent Flyer:** "We travel a lot. I need a stroller that fits in overhead bins. Baby is 8 months." (Target: Joie Pact Pro, UPPAbaby Minu V2)
5. **Colicky Baby:** "My 2-month-old gets really gassy after feeds. Help with bottles." (Target: Dr. Brown's Options+, MAM Anti-Colic)

### Edge Cases (3)
1. **Contradictory Constraints:** "I want a newborn stroller that is super light (under 5kg) but has huge wheels for off-roading and costs under 300 AED." (Expected: Should clarify impossibility or provide best compromise with clear trade-offs)
2. **Growth Spurt/Age Transition:** "My baby is 12 months but weighs 14kg already. Need a car seat." (Expected: Skip 0+ group seats, target 0+/1/2 or Group 1+ with high weight limits like Graco Extend2Fit)
3. **Twins/Multiples:** "I am having twins next month and need a travel system." (Expected: Currently no double strollers in catalog, should gracefully fail or recommend 2x compacts if appropriate, but not hallucinate a double)

### Adversarial/Missing Info (2)
1. **Vague Request:** "What's the best stroller?" (Expected: Should trigger a clarifying question about baby age, lifestyle, or budget rather than randomly guessing)
2. **Out of Scope / Off-Topic:** "Can you recommend a good baby formula brand and a crib?" (Expected: Acknowledge we only cover gear (strollers, car seats, feeding bottles) and redirect to those)

## 2. Evaluation Criteria

When testing the output against the cases above, grade on the following 4 dimensions:

1. **Relevance of Recommendation (1-5):** Did it pick the *right* products based on the catalog constraints? (e.g., didn't suggest a 6-month+ stroller for a newborn).
2. **Grounded Reasoning (1-5):** Is the `why_this_fits` actually tied to the user's prompt, or did it just summarize the product specs?
3. **Handling of Uncertainty (Pass/Fail):** If the prompt lacked crucial info (like baby's age for a car seat), did the LLM ask a clarifying question instead of hallucinating?
4. **Non-Generic Output (Pass/Fail):** Does the response feel like a human expert talking to *this specific* mother, rather than a robotic product brochure?

## 3. Failure Modes

> [!WARNING]
> Watch out for these critical failures during testing. Any occurrence is a blocker for launch.

* **Overconfident Wrong Suggestions:** Suggesting a product that is dangerous or incompatible (e.g., suggesting the Joie Pact Pro for a newborn when it's strictly 6 months+).
* **Generic Reasoning:** The "why" is just a copy-paste of the `key_specs` without referencing the user's situation. Example: "It has a 5-point harness and UPF canopy" (Generic) vs "Since you live in a sunny villa, the UPF canopy is crucial for those afternoon walks" (Personalized).
* **Ignoring Constraints:** Recommending a 2299 AED Doona when the user specifically asked for "budget under 1000".

## 4. Output Examples: BAD vs. GOOD

### Scenario
**User:** "I live in a small apartment and need a stroller for my newborn. I also have a tight budget, maybe around 800 AED."

> [!CAUTION]
> ### ❌ BAD Output (What we want to avoid)
> ```json
> {
>   "understood": "I understand you need a stroller.",
>   "top_picks": [
>     {
>       "product_id": "joie-versatrax",
>       "why_this_fits": "The Joie Versatrax is a great stroller with a 4-wheel suspension and UPF 50+ canopy. It costs 1199 AED.",
>       "watch_out_for": "It weighs 9.8 kg.",
>       "skip_if": "Skip if you don't like Joie."
>     }
>   ]
> }
> ```
> **Why it's bad:**
> - Ignored the budget constraint completely (1199 > 800).
> - Generic reasoning (`why_this_fits` is just specs).
> - Didn't mention the apartment living situation at all.
> - `skip_if` is unhelpful and lazy.
> - Recommended a product that is too heavy and wide for a small apartment.

> [!TIP]
> ### ✅ GOOD Output (What success looks like)
> ```json
> {
>   "understood": "You need a budget-friendly, compact stroller suitable for a newborn that fits easily in an apartment.",
>   "top_picks": [
>     {
>       "product_id": "juniors-venice",
>       "why_this_fits": "At 449 AED, this easily fits your budget and features a full flat recline which is essential for your newborn.",
>       "watch_out_for": "It is quite heavy at 12.1kg and folds to 63cm, so make sure your apartment elevator has enough clearance.",
>       "skip_if": "Skip if you need to carry this up stairs frequently, as the weight will be difficult."
>     },
>     {
>       "product_id": "chicco-my-city-stroller",
>       "why_this_fits": "Priced at 899 AED, it's slightly over your budget but it's much lighter (7.4kg) for apartment living and safe for your newborn.",
>       "watch_out_for": "It requires two hands to fold, meaning you'll need a safe spot to put your baby down first.",
>       "skip_if": "Skip if you absolutely cannot stretch your budget past the 800 AED mark."
>     }
>   ]
> }
> ```
> **Why it's good:**
> - Handled the budget gracefully (found one well under, one slightly over with justification).
> - Explicitly tied the features to the user's constraints (newborn = flat recline, apartment = weight/fold size).
> - Brutally honest `watch_out_for` and `skip_if` that help the user make an informed trade-off.
