import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Simple rule-based nutrition score as a fallback
DEFAULT_FOOD_SCORES = {
    'banana': 9,
    'oats': 9,
    'milk': 6,
    'honey': 5,
    'sugar': 2,
}

def quick_health_score(nutrients: dict) -> int:
    """Return 1–10 score using kcal, sugar, fiber, protein if available."""
    kcal = nutrients.get('energy-kcal_100g') or nutrients.get('energy-kcal') or 0
    sugar = nutrients.get('sugars_100g') or 0
    fiber = nutrients.get('fiber_100g') or 0
    protein = nutrients.get('proteins_100g') or 0
    score = 10
    if kcal and kcal > 400:
        score -= 2
    score += min(2, fiber / 5)
    score += min(2, protein / 10)
    score -= min(3, sugar / 10)
    score = max(1, min(10, int(round(score))))
    return score

# Simple rule-based recipe generator (works offline)
BASE_RECIPES = [
    {
        'name': 'Banana Oatmeal',
        'needs': ['banana', 'oats'],
        'instructions': 'Cook oats in water or milk. Slice banana on top. Optional: cinnamon.'
    },
    {
        'name': 'Veggie Stir Fry',
        'needs': ['onion', 'tomato', 'carrot'],
        'instructions': 'Stir-fry chopped veggies with oil, add salt/pepper. Serve with rice.'
    },
    {
        'name': 'Egg Fried Rice',
        'needs': ['rice', 'egg'],
        'instructions': 'Scramble egg, add cooked rice, soy/seasoning. Mix well.'
    }
]

def rule_based_recipes(pantry: list):
    p = set(x.lower() for x in pantry)
    hits = []
    for r in BASE_RECIPES:
        match = sum(1 for need in r['needs'] if need in p)
        if match:
            hits.append({**r, 'match': match / len(r['needs'])})
    hits.sort(key=lambda x: x['match'], reverse=True)
    return hits[:5]

# Optional: Use OpenAI if key present
def ai_recipes(pantry: list, health_goal: str = 'balanced'):
    if not OPENAI_API_KEY:
        return rule_based_recipes(pantry)
    import json
    import re
    prompt = (
        "Create 3 simple, low-cost recipes using ONLY these pantry items: "
        + ", ".join(pantry)
        + ". Each recipe: name, ingredients list, and 3-step instructions. "
        "Health goal: "
        + health_goal + ". Return JSON list."
    )
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers, json=data, timeout=25
        )
        txt = resp.json()["choices"][0]["message"]["content"]
        # Best effort to parse JSON list from text
        m = re.search(r"\[.*\]", txt, re.S)
        if m:
            return json.loads(m.group(0))
        else:
            # fallback: single recipe
            return [{
                "name": "Chef Special",
                "ingredients": pantry,
                "instructions": txt[:200]
            }]
    except Exception:
        return rule_based_recipes(pantry)