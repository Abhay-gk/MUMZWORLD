# Measurement

## The Single Leading Indicator (Week 1)

**AI Advisor Click-Through Rate to Product Page**

Specifically: the percentage of users who reach the results screen AND click "View on Mumzworld →" on at least one card.

### Why this metric, not others

| Alternative Metric | Why It's Worse |
|---|---|
| Conversion rate (purchase) | Too many downstream variables (price, delivery date, stock). Weak early signal. |
| Session time | Could just mean users are confused and lingering, not engaged. |
| Bounce rate | Inverse signal, harder to act on. |
| Recommendations seen (pageviews) | Measures input, not output — doesn't tell us if AI output was useful. |
| 5-star rating / feedback | Too sparse in Week 1; not representative. |

**Why click-through to product page is the right leading indicator:**
- It's a revealed preference: the user trusted the recommendation enough to take an action
- It's measurable without purchase data (works even in beta with no payment)
- It directly precedes the conversion event — if this improves, conversion follows
- Baseline control: the same metric exists today for standard "You may also like" modules

**Target**: If AI Advisor card CTR > standard product listing CTR by ≥ 2x in Week 1, the personalisation is working. If they're equal or lower, either the recommendations aren't trusted or the UI isn't surfacing the "why" effectively.

---

## The 5% Experiment Design

### Setup

Run a standard A/B test on Mumzworld's product listing pages for **strollers, car seats, and feeding** — the three highest-abandonment categories.

| Group | Experience |
|---|---|
| Control (95%) | Standard Mumzworld product listing page with filters and sort |
| Treatment (5%) | Standard listing page PLUS "Not sure which to pick? Tell me about your situation →" banner that opens the AI Advisor |

**Why 5% and not 50%**: The AI Advisor adds Ollama inference latency (~10–20s locally; faster in cloud). A 5% rollout limits exposure if latency degrades experience. Scale incrementally on positive signal.

**Sample size**: At Mumzworld's scale (estimated 500K monthly gear category views), 5% = ~25,000 sessions per month. Statistically sufficient to detect a 5% lift in CTR with 95% confidence within 2 weeks.

### What "Working" Looks Like

| Signal | Threshold | Action |
|---|---|---|
| AI Advisor open rate (how many clicked the banner) | ≥ 15% of treatment group | Banner placement is visible and compelling |
| Recommendation view → card CTR | ≥ 35% | AI output is trusted and specific enough to act on |
| Advisor CTR vs control listing CTR | ≥ 2x | AI recommendations outperform algorithmic listing ordering |
| Advisor-assisted sessions → purchase within 48h | ≥ 1.5x control purchase rate | Trust translates to conversion |
| Average response time | ≤ 20 seconds | Acceptable wait for personalised result |

### What "Flatlining" Looks Like

| Signal | Interpretation | Fix |
|---|---|---|
| Banner click rate < 8% | Users don't understand or trust the concept | Rewrite CTA copy; test different placements |
| Card CTR < 20% | AI explanations are too generic or not trusted | Audit phi3 outputs; tighten "why this fits" specificity |
| High open rate, low CTR | Users engage but don't act — explanations are interesting but not convincing | Add "used by X moms in your situation" social proof |
| Response time > 25s | Latency kills the UX | Move phi3 to cloud inference; async loading |
| High CTR but low 48h purchase | Advisor sends to wrong products | Audit product_id → URL mapping; check catalog accuracy |

### Second-Order Signal (Week 2+)

Watch **return rate** for products purchased through an AI-Advisor-assisted session vs. control session.

- If return rate for AI-assisted purchases is **lower**, this confirms the core hypothesis: helping the right person find the right product reduces costly returns.
- This is the business case metric that justifies scaling investment beyond a feature to a platform capability.

### Guardrails

- **Do not show the Advisor** to users who have already purchased in this category in the last 30 days (they already decided)
- **Log all AI inputs and outputs** for the first 2 weeks to audit quality — not for personalisation, but to catch phi3 hallucinating product_ids or specs
- **No dark patterns**: the Advisor should only appear as an option, never auto-intercepting the standard browse flow
