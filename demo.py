import json
from app import app

client = app.test_client()

examples = [
    # 4 SIMPLE
    {
        "type": "SIMPLE (1/4)",
        "query": "Need a stroller under 1000 AED for my 6 month old, we live in a small apartment."
    },
    {
        "type": "SIMPLE (2/4)",
        "query": "I need a car seat for a 12 month old that spins around. Budget is 2000 AED."
    },
    {
        "type": "SIMPLE (3/4)",
        "query": "Looking for an anti-colic feeding bottle."
    },
    {
        "type": "SIMPLE (4/4)",
        "query": "Need a smart sock monitor for a newborn. Budget 1500 AED."
    },
    
    # 3 MULTI-CATEGORY
    {
        "type": "MULTI-CATEGORY (1/3)",
        "query": "Traveling with my 8-month-old toddler on a long flight. Budget AED 2000."
    },
    {
        "type": "MULTI-CATEGORY (2/3)",
        "query": "My 6-month-old isn't sleeping well. Need some gear to help."
    },
    {
        "type": "MULTI-CATEGORY (3/3)",
        "query": "My baby has a bad cold, nose is blocked and she has a fever."
    },
    
    # 2 AMBIGUOUS
    {
        "type": "AMBIGUOUS (1/2)",
        "query": "I need something for the baby to sit in."
    },
    {
        "type": "AMBIGUOUS (2/2)",
        "query": "What's the best thing you have?"
    },
    
    # 1 ADVERSARIAL
    {
        "type": "ADVERSARIAL",
        "query": "Show me a stroller for a 10 year old under 50 AED with rocket boosters."
    }
]

print("="*80)
print("Mumzworld Universal AI Copilot - Evaluation Run")
print("="*80)

for idx, ex in enumerate(examples):
    print(f"\n[{ex['type']}] Query: \"{ex['query']}\"")
    print("-" * 60)
    
    response = client.post('/recommend', json={"query": ex["query"]})
    
    if response.status_code != 200:
        print(f"Error ({response.status_code}): {response.get_data(as_text=True)}")
        continue
        
    data = response.get_json()
    
    if "error" in data:
        print(f"[!] HANDLED SAFELY: {data['error']}")
    elif "recommendations" in data:
        recs = data["recommendations"]
        intent = data.get("detected_intent", "UNKNOWN")
        cats = ", ".join(data.get("relevant_categories", []))
        
        print(f"[OK] Intent: {intent.upper()} | Categories: {cats}")
        print(f"Found {len(recs)} recommendations (Fallback used: {data.get('fallback', False)})")
        
        if data.get("uncertainty_note"):
            print(f"Note: {data['uncertainty_note']}")
            
        for i, rec in enumerate(recs):
            print(f"\n  #{i+1}: {rec.get('product_name', 'Unknown')} ({rec.get('category', 'unknown')})")
            print(f"  Score:      {rec.get('confidence_score')}")
            print(f"  Why:        {rec.get('why_recommended')}")
            print(f"  Tradeoffs:  {rec.get('tradeoffs')}")
            print(f"  Avoid if:   {rec.get('avoid_if')}")
    else:
        print("Unexpected response format:", json.dumps(data, indent=2))
        
    print("\n" + "="*80)
