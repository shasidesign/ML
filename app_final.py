"""
StyleIQ — AI-Powered Fashion Intelligence Platform
Flask Backend · MongoDB Atlas · RandomForest ML · OpenAI
IBM Internship Project
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os, traceback
import numpy as np
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "styleiq-secret-2024-change-in-production")

# ── MongoDB ────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/styleiq")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client["styleiq"]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"⚠️  MongoDB connection failed (demo mode active): {e}")
    db = None

def get_col(name):
    return db[name] if db is not None else None

# ── ML Model ───────────────────────────────────────────────────────────────
from ml_models.fashion_predictor import FashionPredictor
predictor = FashionPredictor()

# ── Helpers ────────────────────────────────────────────────────────────────
def serialize(obj):
    if isinstance(obj, list):
        return [serialize(o) for o in obj]
    if isinstance(obj, dict):
        return {k: (str(v) if isinstance(v, ObjectId) else
                    v.isoformat() if isinstance(v, datetime) else
                    serialize(v)) for k, v in obj.items()}
    return obj

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ══════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ══════════════════════════════════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data     = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")
        users    = get_col("users")

        if users is None:                          # demo / no-DB mode
            session["user_id"]  = "demo"
            session["username"] = username or "Demo User"
            return jsonify({"success": True, "username": session["username"]})

        user = users.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user_id"]  = str(user["_id"])
            session["username"] = user["username"]
            return jsonify({"success": True, "username": user["username"]})
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    data     = request.get_json()
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not password or not email:
        return jsonify({"success": False, "error": "All fields required"}), 400

    users = get_col("users")
    if users is None:
        session["user_id"]  = "demo"
        session["username"] = username
        return jsonify({"success": True, "username": username})

    if users.find_one({"username": username}):
        return jsonify({"success": False, "error": "Username already exists"}), 409

    result = users.insert_one({
        "username":   username,
        "email":      email,
        "password":   generate_password_hash(password),
        "created_at": datetime.utcnow(),
    })
    session["user_id"]  = str(result.inserted_id)
    session["username"] = username
    return jsonify({"success": True, "username": username})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ══════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html", user=session.get("username"))

@app.route("/products")
def products():
    return render_template("products.html", user=session.get("username"))

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html", user=session.get("username"))

@app.route("/predict-page")
def predict_page():
    return render_template("predict.html", user=session.get("username"))

@app.route("/wardrobe")
def wardrobe():
    return render_template("wardrobe.html", user=session.get("username"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", username=session.get("username"))


# ══════════════════════════════════════════════════════════════════════════
#  API — PREDICTION
# ══════════════════════════════════════════════════════════════════════════

@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data      = request.get_json()
        height    = float(data.get("height", 170))
        weight    = float(data.get("weight", 65))
        age       = int(data.get("age", 25))
        gender    = data.get("gender", "male")
        body_type = data.get("body_type", "average")

        result = predictor.predict(height, weight, age, gender, body_type)

        col = get_col("predictions")
        if col is not None:
            col.insert_one({
                "user_id":   session.get("user_id", "anonymous"),
                "username":  session.get("username", "Guest"),
                "inputs":    {"height": height, "weight": weight,
                              "age": age, "gender": gender, "body_type": body_type},
                "result":    result,
                "timestamp": datetime.utcnow(),
            })

        return jsonify({"success": True, "prediction": result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/predict/occasion", methods=["POST"])
def predict_occasion():
    try:
        data      = request.get_json()
        height    = float(data.get("height", 170))
        weight    = float(data.get("weight", 65))
        age       = int(data.get("age", 25))
        gender    = data.get("gender", "male")
        body_type = data.get("body_type", "average")
        occasion  = data.get("occasion", "casual")

        base    = predictor.predict(height, weight, age, gender, body_type)
        occ_rec = predictor.occasion_predict(base["style"], gender, occasion)
        base.update({"occasion": occasion, "occasion_outfit": occ_rec})
        return jsonify({"success": True, "prediction": base})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════
#  API — PRODUCTS
# ══════════════════════════════════════════════════════════════════════════

@app.route("/api/products")
def api_products():
    col      = get_col("fashion_products")
    category = request.args.get("category")

    if col is not None and col.count_documents({}) > 0:
        docs = list(col.find({}, {"_id": 0}).limit(24))
    else:
        docs = _demo_products()

    if category and category != "all":
        docs = [p for p in docs if p.get("category") == category]

    return jsonify({"success": True, "products": docs})


@app.route("/api/seed-products", methods=["POST"])
def seed_products():
    col = get_col("fashion_products")
    if col is None:
        return jsonify({"success": False, "error": "No DB connection"}), 503
    if col.count_documents({}) == 0:
        products = _demo_products()
        col.insert_many(products)
        return jsonify({"success": True, "seeded": len(products)})
    return jsonify({"success": True, "message": "Already seeded"})


def _demo_products():
    import random
    items = [
        ("Obsidian Oversized Tee",    "casual",      49,  "Ultra-soft 100% organic cotton. AI-recommended for relaxed body types."),
        ("Midnight Slim Suit",        "formal",      299, "Two-piece tailored wool blend. Perfect confidence fit guaranteed."),
        ("Circuit Cargo Pants",       "streetwear",  89,  "Y2K-inspired utility pants with 8 functional pockets."),
        ("Velocity Training Set",     "athletic",    120, "4-way stretch moisture-wicking fabric. Built for performance."),
        ("Velvet Wrap Dress",         "evening",     175, "Elegant drape silhouette. AI-styled for hourglass body types."),
        ("Linen Capsule Shirt",       "minimalist",  95,  "Relaxed fit, breathable Italian linen. Effortless style."),
        ("Retro Bomber Jacket",       "streetwear",  159, "Premium polyester shell with embroidered details."),
        ("Classic Oxford Shirt",      "formal",      85,  "Crisp poplin weave. Tailored slim fit for a sharp look."),
        ("Cloud Comfort Hoodie",      "casual",      75,  "Heavyweight fleece, dropped shoulder. Cozy and oversized."),
        ("Power Leggings Pro",        "athletic",    68,  "High-waist compression with hidden pocket."),
        ("Satin Evening Blouse",      "evening",     130, "Fluid satin with v-neckline. AI recommends for petite builds."),
        ("Structured Trench Coat",    "minimalist",  220, "Classic silhouette in water-resistant gabardine."),
        ("Acid Wash Denim",           "streetwear",  110, "Vintage-wash slim straight cut. Statement denim redefined."),
        ("Knit Polo Sweater",         "casual",      90,  "Fine merino wool polo collar. Smart casual essential."),
        ("Pleated Dress Trousers",    "formal",      115, "High-rise pleat front in stretch crepe."),
        ("Running Wind Jacket",       "athletic",    98,  "Lightweight ripstop. Packable into chest pocket."),
        ("Sequin Cocktail Dress",     "evening",     195, "Fully sequined mini. AI-rated #1 for evening events."),
        ("Wide-Leg Linen Pants",      "minimalist",  88,  "Relaxed palazzo cut. Neutral earth tones."),
        ("Graphic Print Tee",         "casual",      42,  "Artist collaboration series. Limited drop edition."),
        ("Pinstripe Blazer",          "formal",      185, "Italian pinstripe wool. Structured shoulder, nipped waist."),
        ("Puffer Vest Essential",     "streetwear",  105, "Down-fill utility vest. Layering made effortless."),
        ("Sports Bra Elite",          "athletic",    55,  "Medium impact support. Racerback with mesh panels."),
        ("Slip Maxi Dress",           "evening",     145, "Bias-cut silk-touch satin. Effortlessly glamorous."),
        ("Capsule Turtleneck",        "minimalist",  72,  "Fine-rib cotton turtleneck. The ultimate clean staple."),
    ]
    colors = ["#0a1f10","#1a2e1a","#0d2818","#142b1a","#0f2412","#1e3320","#162a18","#0c2010"]
    badges = ["New","Bestseller","AI Pick","Limited",""]
    return [
        {
            "id":           i + 1,
            "name":         name,
            "category":     cat,
            "price":        price,
            "description":  desc,
            "rating":       round(3.8 + random.random() * 1.2, 1),
            "reviews":      random.randint(12, 340),
            "ai_recommended": random.random() > 0.5,
            "color":        colors[i % len(colors)],
            "badge":        badges[i % 5],
            "sizes":        ["XS","S","M","L","XL"] if cat != "athletic" else ["S","M","L","XL"],
        }
        for i, (name, cat, price, desc) in enumerate(items)
    ]


# ══════════════════════════════════════════════════════════════════════════
#  API — CHATBOT
# ══════════════════════════════════════════════════════════════════════════

FASHION_SYSTEM_PROMPT = """You are StyleIQ's expert AI fashion stylist. Give personalized, 
confident style advice. Be knowledgeable about trends, body types, occasions, and seasonal dressing.
Keep responses concise (2-4 sentences), friendly, and specific. Use fashion terminology naturally.
Always provide actionable outfit suggestions."""

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data    = request.get_json()
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"success": False, "error": "Empty message"}), 400

        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key and openai_key not in ("your-openai-key-here", ""):
            try:
                import openai
                openai.api_key = openai_key
                resp  = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": FASHION_SYSTEM_PROMPT},
                        {"role": "user",   "content": message},
                    ],
                    max_tokens=400,
                    temperature=0.8,
                )
                reply = resp.choices[0].message.content
            except Exception:
                reply = _rule_based_chat(message)
        else:
            reply = _rule_based_chat(message)

        col = get_col("chatbot_history")
        if col is not None:
            col.insert_one({
                "user_id":      session.get("user_id", "anonymous"),
                "user_message": message,
                "ai_reply":     reply,
                "timestamp":    datetime.utcnow(),
            })

        return jsonify({"success": True, "reply": reply})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


def _rule_based_chat(msg):
    m = msg.lower()
    if any(w in m for w in ["winter","cold","snow","freezing"]):
        return "For winter, layer a chunky knit turtleneck under a structured wool overcoat. Pair with tailored trousers and leather Chelsea boots. Dark tones — charcoal, navy, burgundy — create a polished cold-weather look. 🧥"
    if any(w in m for w in ["summer","hot","beach","warm","heat"]):
        return "Summer calls for breathable linen or cotton in soft neutrals and pastels. A linen shirt with wide-leg trousers is effortlessly chic. For beach days, a linen co-ord set is the ultimate summer statement. ☀️"
    if any(w in m for w in ["formal","work","office","interview","professional","business"]):
        return "For a professional setting, a well-fitted blazer is your best asset — pair it with slim trousers and a crisp shirt. Stick to a neutral palette (navy, grey, white) and elevate with leather Oxford shoes. 💼"
    if any(w in m for w in ["gym","workout","athletic","exercise","sport","training"]):
        return "Performance-first athleisure: high-waist compression leggings, a moisture-wicking tank, and a sleek track jacket. Tonal monochrome looks — all-black or all-grey — create a focused, powerful gym aesthetic. 💪"
    if any(w in m for w in ["date","evening","night out","party","dinner","cocktail"]):
        return "For a night out, play with texture — a satin slip dress or tailored dark trousers with a statement top. Add a structured mini bag and heeled boots to complete the look. ✨"
    if any(w in m for w in ["casual","weekend","relax","everyday","brunch"]):
        return "Casual perfection: quality tee tucked into straight-leg denim, with clean white sneakers. The 'quiet luxury' approach — invest in basics with premium fabric and the right fit, and you'll always look effortless. 👟"
    if any(w in m for w in ["streetwear","street","hype","urban","hypebeast"]):
        return "Streetwear is about proportion play — oversized hoodie, slim-fit cargos, and chunky sneakers. Add a statement cap or crossbody bag. Bold graphics and earth tones are dominating this season's street scene. 🔥"
    if any(w in m for w in ["wedding","bride","formal event","gala","black tie"]):
        return "For a wedding or black-tie event, a tailored suit or gown is essential. Men: navy or charcoal suit with pocket square. Women: floor-length gown or elegant midi with statement jewellery. Fit is everything. 🥂"
    if any(w in m for w in ["spring","autumn","fall","season","transition"]):
        return "Transitional dressing is about layering — light jackets, cardigans, and scarves bridge the temperature gap perfectly. A trench coat is the single most versatile piece for spring and autumn wardrobes. 🍂"
    if any(w in m for w in ["colour","color","palette","what to wear with"]):
        return "Start with a neutral base (white, black, beige, grey, navy) and add one accent colour per outfit. Earthy tones — terracotta, olive, camel — are universally flattering and always in style. 🎨"
    if any(w in m for w in ["size","fit","measurements","body type","petite","plus"]):
        return "Great style is 80% about fit. Use StyleIQ's AI Predictor to get your personalized size and style recommendation. A well-fitted $50 outfit will always outperform an ill-fitted designer piece. 📏"
    if any(w in m for w in ["minimalist","capsule","wardrobe","basics","essentials"]):
        return "A capsule wardrobe needs just 10-15 quality pieces: white tee, dark denim, white sneakers, blazer, trench coat, black trousers, camel coat, Oxford shirt, grey knit, and loafers. These create 50+ combinations. ⬜"
    if any(w in m for w in ["budget","cheap","affordable","save money","expensive"]):
        return "Invest where it counts: shoes, coat, and one great blazer. Save on basics like tees and basics from quality high-street brands. Price-per-wear is the best fashion metric — a $200 coat worn 200 times costs $1. 💰"
    return "Style is confidence made visible. The best outfit is one that makes you feel powerful and comfortable simultaneously. Ask me about a specific occasion, season, body type, or colour palette — I'll give you a precise recommendation! 👗"


# ══════════════════════════════════════════════════════════════════════════
#  API — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════

@app.route("/api/dashboard")
@login_required
def api_dashboard():
    user_id   = session.get("user_id")
    preds_col = get_col("predictions")
    favs_col  = get_col("favorites")
    chats_col = get_col("chatbot_history")

    if preds_col is None:
        return jsonify({"success": True, "data": _demo_dashboard()})

    predictions = list(preds_col.find({"user_id": user_id}).sort("timestamp", -1).limit(10))
    favorites   = list(favs_col.find({"user_id": user_id})) if favs_col else []
    chat_count  = chats_col.count_documents({"user_id": user_id}) if chats_col else 0

    style_counts = {}
    for p in predictions:
        s = p.get("result", {}).get("style", "Unknown")
        style_counts[s] = style_counts.get(s, 0) + 1

    return jsonify({
        "success": True,
        "data": {
            "total_predictions": len(predictions),
            "total_favorites":   len(favorites),
            "chat_messages":     chat_count,
            "style_distribution": style_counts,
            "recent_predictions": serialize(predictions[:5]),
        }
    })


def _demo_dashboard():
    return {
        "total_predictions": 12,
        "total_favorites":   7,
        "chat_messages":     24,
        "style_distribution": {"Streetwear":4,"Minimalist":3,"Formal":2,"Casual Chic":2,"Athletic":1},
        "recent_predictions": [
            {"inputs":{"gender":"male","body_type":"athletic"},   "result":{"style":"Streetwear","size":"M","confidence":91},"timestamp":"2024-01-15T10:30:00"},
            {"inputs":{"gender":"female","body_type":"hourglass"},"result":{"style":"Elegant",   "size":"S","confidence":88},"timestamp":"2024-01-14T14:20:00"},
        ],
    }


# ══════════════════════════════════════════════════════════════════════════
#  API — FAVORITES
# ══════════════════════════════════════════════════════════════════════════

@app.route("/api/favorites/toggle", methods=["POST"])
@login_required
def toggle_favorite():
    data       = request.get_json()
    product_id = data.get("product_id")
    user_id    = session.get("user_id")
    favs       = get_col("favorites")

    if favs is None:
        return jsonify({"success": True, "favorited": True})

    existing = favs.find_one({"user_id": user_id, "product_id": product_id})
    if existing:
        favs.delete_one({"_id": existing["_id"]})
        return jsonify({"success": True, "favorited": False})
    favs.insert_one({"user_id": user_id, "product_id": product_id, "timestamp": datetime.utcnow()})
    return jsonify({"success": True, "favorited": True})


# ══════════════════════════════════════════════════════════════════════════
#  API — WARDROBE GENERATOR
# ══════════════════════════════════════════════════════════════════════════

@app.route("/api/wardrobe/week", methods=["POST"])
def wardrobe_week():
    try:
        data      = request.get_json()
        height    = float(data.get("height", 170))
        weight    = float(data.get("weight", 65))
        age       = int(data.get("age", 25))
        gender    = data.get("gender", "male")
        body_type = data.get("body_type", "average")
        occasion  = data.get("occasion", "mixed")

        prediction = predictor.predict(height, weight, age, gender, body_type)
        style      = prediction["style"]
        size       = prediction["size"]

        days    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        occ_map = {
            "casual": ["casual","casual","casual","casual","casual","weekend","weekend"],
            "work":   ["work","work","work","work","work","casual","casual"],
            "formal": ["formal","formal","formal","formal","formal","smart_casual","casual"],
            "mixed":  ["work","casual","work","formal","casual","evening","weekend"],
        }
        schedule = occ_map.get(occasion, occ_map["mixed"])
        outfits  = predictor.generate_week_outfits(style, gender, schedule, size)

        week_plan = [
            {"day": days[i], "occasion": schedule[i].replace("_"," ").title(),
             "outfit": outfits[i], "style": style}
            for i in range(7)
        ]

        return jsonify({"success": True, "week_plan": week_plan,
                        "style": style, "size": size, "confidence": prediction["confidence"]})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════
#  API — PROFILE
# ══════════════════════════════════════════════════════════════════════════

@app.route("/api/profile/save", methods=["POST"])
@login_required
def save_profile():
    data    = request.get_json()
    user_id = session.get("user_id")
    users   = get_col("users")
    if users and user_id != "demo":
        try:
            users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"profile": data, "updated_at": datetime.utcnow()}},
                upsert=True,
            )
        except Exception:
            pass
    return jsonify({"success": True})


@app.route("/api/profile/change-password", methods=["POST"])
@login_required
def change_password():
    data    = request.get_json()
    cur_pwd = data.get("current_password", "")
    new_pwd = data.get("new_password", "")
    users   = get_col("users")

    if users is None:
        return jsonify({"success": True})   # demo mode

    user_id = session.get("user_id")
    try:
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user or not check_password_hash(user["password"], cur_pwd):
            return jsonify({"success": False, "error": "Current password is incorrect"}), 401
        users.update_one({"_id": ObjectId(user_id)},
                         {"$set": {"password": generate_password_hash(new_pwd)}})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════
#  ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("404.html", error="500"), 500


# ══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
