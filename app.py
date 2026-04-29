import json
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ─── Load catalog once at startup ─────────────────────────────────────────────
with open("products.json", encoding="utf-8") as f:
    CATALOG = json.load(f)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "phi3:latest"

# Kept intentionally short — phi3 loses instruction-following with long prompts
SYSTEM_PROMPT = """You are Aisha, the universal AI Shopping Copilot for Mumzworld.
Your goal is to map the mother's query to relevant categories, detect her intent, and provide highly grounded cross-category recommendations.
If a mother says something unrelated or stressful, respond warmly in the `conversational_response` field.

RULES:
1. You MUST ONLY output valid JSON. No markdown, no intro/outro text.
2. If the user is asking for general parenting advice or medical help (e.g. 'baby is vomiting'), provide a helpful, empathetic response in `conversational_response`. If it's a medical issue, you MUST advise them to consult a pediatrician immediately. Leave `recommendations` empty.
3. If it IS a shopping query, map the intent and pick up to 3 products from the provided catalog.
4. "best_for" must be the product's exact use_case.
5. "avoid_if" must be the product's exact avoid_if warning.
6. If no products in the catalog fit safely, leave recommendations empty and explain why in `uncertainty_note`.

Return this exact JSON schema only:
{
  "detected_intent": "buying, exploring, troubleshooting, or chatting",
  "relevant_categories": ["array", "of", "categories"],
  "recommendations": [
    {
      "product_name": "exact name from catalog",
      "category": "product category",
      "why_recommended": "text",
      "tradeoffs": "text",
      "best_for": "text",
      "avoid_if": "text",
      "confidence_score": 0.9
    }
  ],
  "uncertainty_note": "A friendly message if you need more details. If everything is clear, leave empty.",
  "conversational_response": "Only populate if the query is general/non-shopping advice."
}"""

# ─── Rule-based pre-filter ─────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "strollers": ["stroller", "pram", "pushchair", "buggy", "walk", "park"],
    "car_seats": ["car seat", "carseat", "infant seat", "booster", "drive", "car"],
    "feeding": ["bottle", "feed", "high chair", "pump", "colic", "weaning"],
    "nursery": ["sleep", "crib", "monitor", "bassinet", "night", "wake"],
    "health": ["sick", "fever", "thermometer", "nose", "crying", "teething"],
    "travel": ["flight", "plane", "holiday", "travel", "trip", "portable", "carrier"],
    "diapers": ["diaper", "nappy", "wipes", "pampers", "huggies", "potty"],
    "toys": ["toy", "play", "blocks", "learn", "rattle", "educational"],
    "clothing": ["clothes", "onesie", "pajamas", "cotton", "wear", "shirt", "pants"]
}

TEXT_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12
}

def extract_constraints(query: str) -> dict:
    q = query.lower()
    constraints = {}

    # Budget — supports AED, INR/₹ (converted at ~4 INR/AED)
    budget_match = re.search(r'aed\s*([\d,]+)', q)
    if budget_match:
        constraints["budget_max"] = int(budget_match.group(1).replace(",", ""))
    else:
        budget_match = re.search(r'([\d,]+)\s*(?:aed|dirhams?|dhs?)', q)
        if budget_match:
            constraints["budget_max"] = int(budget_match.group(1).replace(",", ""))
        else:
            inr_match = re.search(r'(?:inr|rs\.?|₹)\s*([\d,]+)', q)
            if not inr_match:
                inr_match = re.search(r'([\d,]+)\s*(?:inr|rupees?|rs\.?)', q)
            if inr_match:
                inr = int(inr_match.group(1).replace(",", ""))
                constraints["budget_max"] = int(inr / 22.5)  # exact AED equivalent (1 AED ~ 22.5 INR)
                constraints["currency_note"] = f"₹{inr:,} (~AED {int(inr/22.5)})"

    # Baby age in months (handles digits and text)
    months_match = re.search(r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(?:-\s*)?month", q)
    if months_match:
        val = months_match.group(1)
        constraints["baby_age_months"] = int(val) if val.isdigit() else TEXT_NUMBERS.get(val, 0)
    else:
        years_match = re.search(r"(\d+|one|two|three|four|five)\s*(?:-\s*)?year", q)
        if years_match:
            val = years_match.group(1)
            years = int(val) if val.isdigit() else TEXT_NUMBERS.get(val, 0)
            constraints["baby_age_months"] = years * 12

    # Detect multi-category from keywords
    matched_cats = set()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            matched_cats.add(cat)
    if matched_cats:
        constraints["categories"] = list(matched_cats)

    return constraints

def pre_filter(catalog: list, constraints: dict, category_override: str = None) -> list:
    results = catalog

    # Multi-category filtering
    cats = [category_override] if category_override else constraints.get("categories", [])
    if cats:
        results = [p for p in results if p["category"] in cats]

    # In-stock only
    results = [p for p in results if p.get("in_stock", True)]

    # Budget with 15% flex (don't be too strict — let LLM justify value)
    if "budget_max" in constraints:
        limit = constraints["budget_max"] * 1.15
        results = [p for p in results if p["price_aed"] <= limit]

    # Age filter
    if "baby_age_months" in constraints:
        age = constraints["baby_age_months"]
        results = [
            p for p in results
            if p.get("age_min_months", 0) <= age
            <= p.get("age_max_years", 20) * 12
        ]

    # Return max 15 candidates to keep prompt lean
    return results[:15]


def slim_product(p: dict) -> dict:
    """Strip heavy/redundant fields before sending to LLM."""
    return {
        "id": p["id"],
        "product_name": p.get("product_name", p.get("name")),
        "category": p["category"],
        "price_range": p.get("price_range", ""),
        "age_range": p.get("age_range", ""),
        "key_features": p.get("key_features", []),
        "use_case": p.get("use_case", ""),
        "avoid_if": p.get("avoid_if", "")
    }


# ─── Ollama call ───────────────────────────────────────────────────────────────

def extract_json_from_text(text: str):
    """Multi-strategy JSON extraction — handles phi3 quirks."""
    if not text:
        return None
    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Strategy 2: strip markdown code fences
    fence = re.search(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1))
        except Exception:
            pass
    # Strategy 3: find the outermost {...} block
    brace = re.search(r'(\{[\s\S]*\})', text)
    if brace:
        try:
            return json.loads(brace.group(1))
        except Exception:
            pass
    return None


def call_ollama(user_prompt: str, retries: int = 1):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 2048,  # phi3 needs more room for 3-pick JSON
        },
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        raw_content = resp.json().get("message", {}).get("content", "")
        result = extract_json_from_text(raw_content)
        if result:
            return result
        print(f"[Ollama parse failed] raw: {raw_content[:200]}")
        if retries > 0:
            return call_ollama(user_prompt, retries - 1)
        return None
    except requests.HTTPError as exc:
        print(f"[Ollama HTTP {exc.response.status_code}] {exc.response.text[:200]}")
        if retries > 0:
            return call_ollama(user_prompt, retries - 1)
        return None
    except Exception as exc:
        print(f"[Ollama error] {type(exc).__name__}: {exc}")
        if retries > 0:
            return call_ollama(user_prompt, retries - 1)
        return None


# ─── Fallback: rule-based PERSONALISED top-3 ──────────────────────────────────
# This runs when phi3 cannot be reached or returns bad JSON.
# It uses product attributes + extracted constraints to generate specific reasoning.
# NOT generic — each explanation references the user's actual situation.

def personalised_why(p: dict, constraints: dict) -> str:
    """Generate a context-aware explanation without the LLM."""
    parts = []
    age = constraints.get("baby_age_months")
    budget = constraints.get("budget_max")
    cat = p.get("category", "")

    if cat == "stroller":
        if p.get("suitable_for_apartment"):
            w = p.get("folded_width_cm")
            parts.append(
                f"Folds to {w}cm — comfortably fits standard elevator doors."
                if w else "Designed for apartment and elevator use."
            )
        if p.get("one_hand_fold"):
            parts.append("One-hand fold means you can hold your baby while folding it.")
        if age is not None and p.get("age_min_months", 0) == 0:
            parts.append(f"Safe from birth, so it's right for your {age}-month-old.")
        max_kg = p.get("weight_max_kg")
        if max_kg:
            parts.append(f"Supports up to {max_kg} kg — won't need replacing for several years.")
    elif cat == "car_seat":
        if p.get("isofix"):
            base_note = " (base included)" if p.get("isofix_base_included") else " (base sold separately)"
            parts.append(f"ISOFIX{base_note} — secure click-in installation, no guesswork.")
        if p.get("rotation"):
            parts.append("360° rotation makes lifting baby in and out much easier on your back.")
        if age is not None and p.get("age_min_months", 0) == 0:
            parts.append(f"Suitable from birth — right for your {age}-month-old.")
        max_yrs = p.get("age_max_years")
        if max_yrs and max_yrs >= 4:
            parts.append(f"Lasts to {max_yrs} years — no need to buy another seat soon.")
    elif cat == "feeding":
        if p.get("anti_colic"):
            parts.append("Anti-colic design reduces gas and fussiness after feeds.")
        specs = p.get("key_specs", "")
        if specs:
            parts.append(specs[:120])

    if budget and p.get("price_aed", 0) <= budget * 0.85:
        parts.append(f"At AED {p['price_aed']}, it's well within your budget.")
    elif budget and p.get("price_aed", 0) <= budget:
        parts.append(f"AED {p['price_aed']} — just fits your budget.")

    if not parts:
        parts.append(p.get("key_specs", "Strong option in this category.")[:150])

    return " ".join(parts[:2])  # max 2 sentences


def fallback_picks(candidates: list, constraints: dict = None) -> list:
    constraints = constraints or {}
    # Score: apartment suitability + rating, weighted by user context
    def score(p):
        s = p.get("rating", 3.5)
        if constraints.get("category") == "stroller":
            if p.get("suitable_for_apartment"):  s += 0.5
            if p.get("one_hand_fold"):           s += 0.3
            if p.get("folded_width_cm", 99) < 50: s += 0.3
        elif constraints.get("category") == "car_seat":
            if p.get("isofix_base_included"):    s += 0.5
            if p.get("rotation"):                s += 0.3
        return s

    top = sorted(candidates, key=score, reverse=True)[:3]
    return {
        "detected_intent": "exploring",
        "relevant_categories": list(set(p["category"] for p in top)),
        "uncertainty_note": "",
        "recommendations": [
            {
                "product_name": p["product_name"],
                "category": p["category"],
                "why_recommended": p.get("use_case", "Highly rated by Mumzworld mothers for this exact need."),
                "tradeoffs": "We always recommend checking the product specs to ensure the perfect fit for your baby.",
                "best_for": p.get("use_case", "Everyday use"),
                "avoid_if": p.get("avoid_if", ""),
                "confidence_score": 0.6
            }
            for p in top
        ]
    }


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    category_override = data.get("category") or None

    if not query:
        return jsonify({"error": "Please describe your situation first."}), 400

    # 0. Catch pure greetings / chitchat BEFORE any product logic
    q_words = query.lower().split()
    GREETINGS = {"hi", "hello", "hey", "hiya", "sup", "yo", "howdy"}
    if len(q_words) <= 3 and any(w in GREETINGS for w in q_words):
        return jsonify({
            "chat_response": "Hi there! 👋 I'm Aisha, your Mumzworld AI Advisor. Tell me about your baby and your lifestyle — budget, age, what challenge you're facing — and I'll find the perfect fit! 🌸"
        })

    # 0b. Catch medical/distress queries BEFORE any product logic
    DISTRESS_WORDS = ["vomit", "vomiting", "fever", "sick", "diarrhea", "choking",
                      "rash", "bleeding", "doctor", "hospital", "pain", "hurt",
                      "emergency", "breathe", "breathing", "seizure", "faint"]
    q_lower_check = query.lower()
    if any(w in q_lower_check for w in DISTRESS_WORDS):
        return jsonify({
            "chat_response": "I hear you, and I know how frightening it is when your little one isn't well. 💛 Please consult a pediatrician or call your healthcare provider immediately — your baby's health always comes first. Once everything is okay, I'm here to help with any baby gear you need! ❤️"
        })

    # 1. Rule layer
    constraints = extract_constraints(query)
    if category_override:
        constraints["category"] = category_override

    candidates = pre_filter(CATALOG, constraints, category_override)

    # If no products match the strict constraints, do not guess — tell the user honestly
    if not candidates and not any(kw in query.lower() for kw in ["how to", "my baby", "help", "sick"]):
        return jsonify({
            "error": "I couldn't find any products in our catalog that match your strict budget and criteria. Try slightly increasing your budget or changing your requirements."
        })

    # 2. Build LLM prompt
    catalog_json = json.dumps([slim_product(p) for p in candidates], indent=2)
    user_prompt = (
        f"Mother's situation:\n{query}\n\n"
        f"Available products to choose from:\n{catalog_json}"
    )

    # 3. LLM call
    result = call_ollama(user_prompt)

    # 4. Build full product map for frontend rendering
    product_map = {p["id"]: p for p in candidates}
    name_map = {p["product_name"]: p for p in candidates}

    if result and result.get("conversational_response"):
        return jsonify({
            "chat_response": result["conversational_response"]
        })

    # 5. Handle insufficient data
    if result and "recommendations" in result and not result["recommendations"]:
        note = result.get("uncertainty_note", "")
        return jsonify({
            "error": f"I couldn't find exact matches for those criteria. {note}",
            "fallback": False
        })

    # 6. Validate picks exist in catalog
    if result and "recommendations" in result:
        valid_picks = []
        for pick in result["recommendations"]:
            name = pick.get("product_name")
            if name in name_map:
                pick["product_id"] = name_map[name]["id"]
                valid_picks.append(pick)
        
        if valid_picks:
            return jsonify({
                "detected_intent": result.get("detected_intent", "exploring"),
                "relevant_categories": result.get("relevant_categories", []),
                "uncertainty_note": result.get("uncertainty_note", ""),
                "recommendations": valid_picks[:3],
                "products": product_map,
                "fallback": False,
                "constraints": constraints,
            })

    # 7. Graceful fallback — conversational & medical catch
    q_lower = query.lower()
    
    # Only block if it's a pure greeting AND LLM failed
    if len(query.split()) <= 3 and any(g in q_lower for g in ["hi", "hello", "hey", "help"]):
        return jsonify({"error": "Hi there! 👋 I'm Aisha, your Mumzworld AI Advisor. How can I help you find the perfect baby gear today?"})

    # If LLM failed, check for medical/advice phrasing before blindly recommending products
    distress_words = ["fever", "vomit", "sick", "diarrhea", "choking", "rash", "bleeding", "doctor", "hospital", "pain", "hurt", "crying"]
    if any(w in q_lower for w in distress_words):
        return jsonify({
            "chat_response": "I hear you, and I know how stressful it can be when your little one isn't well. Please consult a pediatrician or healthcare professional immediately. Your baby's health is the top priority! ❤️"
        })

    # If LLM failed and we have ZERO extracted constraints
    if not constraints:
        return jsonify({
            "error": "I hear you! Motherhood is a journey, and I'm here to make at least the shopping part easier. 🌸 What are you looking for today?"
        })

    # 8. Graceful fallback — personalised using rule layer
    fallback_data = fallback_picks(candidates, constraints)
    for pick in fallback_data["recommendations"]:
        pick["product_id"] = name_map[pick["product_name"]]["id"]

    return jsonify({
        "detected_intent": fallback_data["detected_intent"],
        "relevant_categories": fallback_data["relevant_categories"],
        "uncertainty_note": fallback_data["uncertainty_note"],
        "recommendations": fallback_data["recommendations"],
        "products": product_map,
        "fallback": True,
        "constraints": constraints,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
