from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import SessionLocal, User, PantryItem, Donation, Lesson
from ai import ai_recipes, quick_health_score
import requests

app = Flask(__name__)
CORS(app)

# ---------- Pages ---------
@app.get('/')
def home():
    return render_template('index.html')

# ---------- Helpers ---------
OFF_URL = 'https://world.openfoodfacts.org/api/v2/product/'
SEARCH_URL = 'https://world.openfoodfacts.org/cgi/search.pl'

# Nutrition by barcode
@app.get('/api/scan/<barcode>')
def scan_barcode(barcode):
    try:
        r = requests.get(OFF_URL + str(barcode) + '.json', timeout=10)
        data = r.json()
        product = data.get('product', {})
        nutrients = product.get('nutriments', {})
        score = quick_health_score(nutrients)
        return jsonify({
            'status': 'ok',
            'name': product.get('product_name', 'Unknown'),
            'brand': product.get('brands', ''),
            'nutriments': nutrients,
            'health_score': score
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Search by name (first match)
@app.get('/api/food')
def food_search():
    q = request.args.get('q', '')
    params = {'search_terms': q, 'search_simple': 1, 'action': 'process', 'json': 1, 'page_size': 1}
    r = requests.get(SEARCH_URL, params=params, timeout=10)
    d = r.json()
    if d.get('products'):
        p = d['products'][0]
        nutrients = p.get('nutriments', {})
        score = quick_health_score(nutrients)
        return jsonify({'status': 'ok', 'name': p.get('product_name', 'Unknown'),
                        'nutriments': nutrients, 'health_score': score})
    return jsonify({'status': 'not_found'})

# Pantry management (single demo user id=1)
@app.post('/api/pantry')
def add_pantry():
    name = (request.json or {}).get('name', '').strip()
    qty = float((request.json or {}).get('quantity', 1))
    db = SessionLocal()
    user = db.get(User, 1)  # Updated for SQLAlchemy 2.x
    if not user:
        user = User(id=1, email='demo@local', name='Demo')
        db.add(user)
        db.commit()
        db.refresh(user)
    item = PantryItem(user_id=user.id, name=name, quantity=qty)
    db.add(item)
    db.commit()
    out = {'id': item.id, 'name': item.name, 'quantity': item.quantity}
    db.close()
    return jsonify(out), 201

@app.get('/api/pantry')
def list_pantry():
    db = SessionLocal()
    items = db.query(PantryItem).filter_by(user_id=1).all()
    out = [{'id': i.id, 'name': i.name, 'quantity': i.quantity} for i in items]
    db.close()
    return jsonify(out)

@app.delete('/api/pantry/<int:item_id>')
def delete_pantry(item_id):
    db = SessionLocal()
    i = db.get(PantryItem, item_id)  # Updated for SQLAlchemy 2.x
    if i:
        db.delete(i)
        db.commit()
    db.close()
    return ('', 204)

# AI Recipes
@app.post('/api/recipes')
def recipes_api():
    data = request.json or {}
    pantry = data.get('pantry', [])
    goal = data.get('goal', 'balanced')
    recs = ai_recipes(pantry, goal)
    return jsonify(recs)

# Donations
@app.post('/api/donations')
def create_donation():
    d = request.json or {}
    db = SessionLocal()
    donation = Donation(
        user_name=d.get('user_name', 'Anonymous'),
        item=d.get('item', ''),
        quantity=d.get('quantity', '1'),
        lat=float(d.get('lat', 0.0)),
        lng=float(d.get('lng', 0.0)),
        note=d.get('note', '')
    )
    db.add(donation)
    db.commit()
    out = {'id': donation.id}
    db.close()
    return jsonify(out), 201

@app.get('/api/donations')
def list_donations():
    db = SessionLocal()
    rows = db.query(Donation).all()
    out = [
        {'id': r.id, 'user_name': r.user_name, 'item': r.item, 'quantity': r.quantity, 'lat': r.lat, 'lng': r.lng, 'note': r.note}
        for r in rows
    ]
    db.close()
    return jsonify(out)

# Lessons
@app.get('/api/lessons')
def lessons():
    db = SessionLocal()
    rows = db.query(Lesson).all()
    out = [{'id': r.id, 'title': r.title, 'content': r.content} for r in rows]
    db.close()
    return jsonify(out)

@app.route("/search")
def search():
    query = request.args.get("query", "").lower()
    if not query:
        return jsonify({"error": "Missing query"}), 400

    # 1. Try live API first
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1
    }

    try:
        r = requests.get(
            url,
            params=params,
            headers={"User-Agent": "NutriScan Hackathon App"},
            timeout=6
        )
        r.raise_for_status()
        data = r.json()

        # If API returned products, use them
        products = data.get("products", [])
        if products:
            return jsonify(products[:5])
    except Exception as e:
        print("⚠️ API failed, using fallback:", e)

    # 2. Fallback mock data (always works for demo)
    fallback_data = {
        "banana": [{
            "product_name": "Banana",
            "brands": "Generic",
            "nutriments": {
                "energy-kcal_100g": 89,
                "carbohydrates_100g": 23,
                "sugars_100g": 12,
                "fiber_100g": 2.6
            }
        }],
        "milk": [{
            "product_name": "Fresh Milk",
            "brands": "Generic",
            "nutriments": {
                "energy-kcal_100g": 42,
                "proteins_100g": 3.4,
                "fats_100g": 1.0,
                "calcium_100g": 120
            }
        }]
    }

    if query in fallback_data:
        return jsonify(fallback_data[query])

    return jsonify([{
        "product_name": query.title(),
        "brands": "Demo Data",
        "nutriments": {
            "energy-kcal_100g": 100,
            "proteins_100g": 2,
            "fats_100g": 1,
            "carbohydrates_100g": 20
        }
    }])

@app.route("/recipes", methods=["POST"])
def recipes():
    try:
        data = request.get_json() or {}
        items = data.get("items", [])
        if not items:
            return jsonify({"error": "No items provided"}), 400

        # --- 1. Try AI (if available) ---
        try:
            import openai
            from dotenv import load_dotenv
            import os

            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")

            if api_key:
                openai.api_key = api_key
                prompt = f"Suggest 3 simple, healthy recipes using these ingredients: {', '.join(items)}."

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=150
                )

                recipes_text = response["choices"][0]["message"]["content"]
                return jsonify({"recipes": recipes_text.split("\n")})
        except Exception as e:
            print("⚠️ AI failed, using fallback recipes:", e)

        # --- 2. Fallback Mock Recipes ---
        fallback_recipes = {
            "banana": [
                "Banana Smoothie: Blend banana, milk, and honey.",
                "Banana Pancakes: Mash banana into pancake batter.",
                "Frozen Banana Pops: Dip in chocolate and freeze."
            ],
            "milk": [
                "Milkshake: Blend milk with ice cream.",
                "Golden Milk: Heat milk with turmeric and honey.",
                "Hot Cocoa: Mix milk with cocoa powder."
            ],
            "oats": [
                "Overnight Oats: Soak oats in milk overnight.",
                "Oatmeal: Cook oats with milk, top with fruit.",
                "Oat Cookies: Bake oats with banana and chocolate chips."
            ]
        }

        # If any known ingredient matches, return those recipes
        for item in items:
            if item.lower() in fallback_recipes:
                return jsonify({"recipes": fallback_recipes[item.lower()]})

        # Otherwise return a generic recipe
        return jsonify({"recipes": [
            f"Simple {items[0].title()} Stir Fry: sauté with oil and spices.",
            f"{items[0].title()} Salad: mix with greens and dressing.",
            f"{items[0].title()} Wrap: roll in flatbread with veggies."
        ]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    import stripe
import os
from flask import Flask, request, jsonify

# Load keys from environment variables (add these in your .env file)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "NutriScan Donation"
                    },
                    "unit_amount": 500,  # $5.00 donation
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://127.0.0.1:5000/success",
            cancel_url="http://127.0.0.1:5000/cancel",
        )
        return jsonify({"id": checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
