import requests, json, re

def extract_json(text):
    """Try multiple strategies to get JSON from phi3 output."""
    # 1. Direct parse
    try:
        return json.loads(text)
    except: pass
    
    # 2. Strip markdown code fences
    code_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_match:
        try: return json.loads(code_match.group(1))
        except: pass
    
    # 3. Find first {...} block
    brace_match = re.search(r'(\{.*\})', text, re.DOTALL)
    if brace_match:
        try: return json.loads(brace_match.group(1))
        except: pass
    
    return None

# Minimal prompt — teach phi3 exactly what to do
SYSTEM = """You are a baby product advisor. You MUST respond with ONLY a JSON object. No explanations before or after. No markdown. Pure JSON only.

JSON structure required:
{"top_picks": [{"product_id": "string", "why_this_fits": "string", "watch_out_for": "string", "skip_if": "string"}]}"""

USER = """Mother: Baby 3 months, apartment elevator, budget 800-1200 AED, need stroller.

Products:
[
  {"id": "joie-versatrax", "name": "Joie Versatrax", "price_aed": 1199, "age_min_months": 0, "folded_width_cm": 44, "one_hand_fold": true, "key_specs": "From birth, full recline, folds to 44cm, 9.8kg"},
  {"id": "chicco-my-city-stroller", "name": "Chicco MyCity", "price_aed": 899, "age_min_months": 0, "folded_width_cm": 52, "one_hand_fold": false, "key_specs": "From birth, 7.4kg lightweight, 52cm fold"},
  {"id": "joie-tourist", "name": "Joie Tourist", "price_aed": 799, "age_min_months": 6, "folded_width_cm": 32, "one_hand_fold": true, "key_specs": "6+ months only, folds to 32cm, 7kg"}
]

Pick 2 best products. Return ONLY JSON."""

payload = {
    "model": "phi3:latest",
    "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER}
    ],
    "format": "json",
    "stream": False,
    "options": {"temperature": 0.1, "num_predict": 600}
}

print("Sending to Ollama...")
r = requests.post("http://localhost:11434/api/chat", json=payload, timeout=90)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    raw = data.get("message", {}).get("content", "")
    print(f"\nRAW ({len(raw)} chars):")
    print(repr(raw))
    
    parsed = extract_json(raw)
    if parsed:
        print("\n✅ PARSED SUCCESSFULLY:")
        print(json.dumps(parsed, indent=2))
    else:
        print("\n❌ PARSE FAILED")
else:
    print(r.text[:300])
