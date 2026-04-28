# 7. Failure Modes

Implementing an LLM introduces specific risks that standard software does not face. Here are 5 real failure risks for this implementation and how they manifest:

1. **Overconfidence in Incorrect Specs:** 
   The model might confidently hallucinate a feature that doesn't exist to please the user. For example, telling a mother that a 12kg stroller "is extremely lightweight and perfect for your bad back." This destroys trust immediately.

2. **Generic Reasoning (The "Brochure" Problem):** 
   Instead of applying the product to the mother's life, the model simply regurgitates the product description. 
   *Bad:* "I recommend this because it has a 5-point harness." 
   *Good:* "Since your baby is very active, the 5-point harness ensures he won't climb out."

3. **Ignoring Hard Constraints (Budget/Age):** 
   Small models like Phi-3 often suffer from "attention drift" in long contexts and may recommend a 3000 AED car seat when the user explicitly asked for "under 500 AED", simply because the 3000 AED seat matched all other semantic criteria perfectly. (Mitigated by the rule-based pre-filter).

4. **Hallucinated Compatibility:** 
   In baby gear, compatibility is strict (e.g., Car Seat X only fits Stroller Y with Adapter Z). The model might confidently tell a user to "buy the Joie Versatrax to go with your Maxi-Cosi car seat" without realizing they are incompatible out-of-the-box. This leads to high return rates.

5. **Latency Abandonment:** 
   Running generative AI takes time. If the time-to-first-token is > 10 seconds (common on local hardware or overloaded cloud deployments), the mother will assume the site is broken and abandon the page before seeing the highly personalized result.
