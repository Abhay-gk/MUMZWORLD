# Success Metrics & Experimentation

## 1. The ONE Leading Indicator of Success (Week 1)

**AI Advisor Click-Through Rate (CTR) to Product Page**
Specifically: The percentage of users who reach the AI Advisor's result screen and click "View on Mumzworld →" on at least one recommended product.

**Why this metric?**
* **Revealed Preference:** It proves the user trusted the AI's personalized reasoning enough to take action.
* **Early Signal:** You don't have to wait for the full purchase cycle (which can take days for high-ticket items like strollers).
* **Baseline Exists:** We can directly compare this to the CTR of standard product listing pages or "You may also like" modules.

## 2. Running the 5% Experiment

**Setup:** Run an A/B test on the product listing pages for the highest-abandonment categories (e.g., strollers, car seats).
* **Control (95%):** Standard Mumzworld category page with normal filters.
* **Treatment (5%):** Standard category page + an intercept banner: *"Not sure which to pick? Tell me your situation →"* which opens the AI Advisor.

**Why 5%?**
LLM inference (especially local Ollama) adds latency. A 5% rollout bounds the risk. At Mumzworld's scale, 5% of category traffic is statistically significant enough to detect a 5% lift in CTR within 2 weeks without risking the core revenue stream if the model hallucinates or is too slow.

## 3. Metric Improvement Indicating Success

The experiment is a success if we see:
1. **Advisor CTR vs. Control:** The AI Advisor recommendation card CTR is **≥ 2x** the standard product listing CTR. (This proves personalization beats generic sorting).
2. **Engagement Rate:** **≥ 15%** of users in the treatment group click the banner to use the AI Advisor.
3. **Downstream Conversion:** Advisor-assisted sessions show a **≥ 1.5x** purchase rate within 48 hours compared to control sessions.

## 4. Failure Results

The experiment has failed (or requires major iteration) if:
1. **Low Engagement (Banner Click < 8%):** Users don't understand the value proposition or don't want to chat with an AI.
2. **Flat CTR (Card CTR < 20%):** Users use the tool but don't click the products. This means the AI's reasoning (`why_this_fits`) is too generic, unconvincing, or it recommended the wrong items.
3. **High Latency Abandonment:** Time to first token or total response time exceeds 15-20 seconds, causing users to close the modal before the recommendations load.
4. **Increased Return Rate (Week 4+):** If products bought via the AI Advisor are returned *more* often than control, the AI is confidently recommending incompatible items.
