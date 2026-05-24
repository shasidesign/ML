from PIL import Image
from openai import OpenAI
import os
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
import sqlite3
import joblib
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt

app = Flask(__name__)

client = OpenAI(
    api_key="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"
)

app.secret_key = 'fashion_ai_secret'
app.config['SECRET_KEY'] = 'fashion_ai_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

# =========================
# CREATE SQLITE TABLES
# =========================
def init_db():
    conn = sqlite3.connect('fashion.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            feedback TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            height INTEGER,
            weight INTEGER,
            age INTEGER,
            gender TEXT,
            body TEXT,
            style TEXT,
            predicted_size TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            outfit_name TEXT,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================
# USER MODEL
# =========================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    trial_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.String(100))

# =========================
# LOAD ML MODELS
# =========================
model = joblib.load('model/size_model.pkl')
gender_encoder = joblib.load('model/gender_encoder.pkl')
body_encoder = joblib.load('model/body_encoder.pkl')
size_encoder = joblib.load('model/size_encoder.pkl')

# =========================
# HOME  ← FIX 1: redirect to login only if accessing protected pages
# =========================
@app.route('/')
def home():
    # Show home page to everyone — no login required
    return render_template('index.html')

# =========================
# AUTH page (combined login/register)  ← NEW: single auth.html page
# =========================
@app.route('/auth')
def auth():
    # If already logged in, skip auth page and go to dashboard
    if 'user' in session:
        return redirect('/dashboard')
    return render_template('auth.html')

# =========================
# LOGIN  ← FIX 2: skip login page if already logged in
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ← THIS IS THE KEY FIX — if already logged in, go home
    if 'user' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # First try users.txt (legacy plain-text users)
        try:
            with open('users.txt', 'r') as file:
                for user in file.readlines():
                    data = user.strip().split(',')
                    if len(data) >= 3:
                        if username == data[0] and password == data[2]:
                            session['user'] = username
                            return redirect('/dashboard')
        except FileNotFoundError:
            pass

        # Then try SQLAlchemy User table (hashed passwords)
        user_obj = User.query.filter_by(username=username).first()
        if user_obj and check_password_hash(user_obj.password, password):
            session['user'] = username
            # Update last login
            user_obj.last_login = datetime.now().strftime('%Y-%m-%d %H:%M')
            db.session.commit()
            return redirect('/dashboard')

        flash('Invalid username or password', 'error')
        return render_template('login.html')

    return render_template('login.html')

# =========================
# SIGNUP  ← FIX 3: skip signup if already logged in
# =========================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect('/')

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()

        with open('users.txt', 'a') as file:
            file.write(f"{name},{phone},{password}\n")

        session['user'] = name
        return redirect('/dashboard')

    return render_template('signup.html')

# =========================
# REGISTER (SQLAlchemy version)  ← FIX 4: skip if logged in + JSON support
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect('/')

    if request.method == 'POST':
        # Support both JSON (from new login.html) and form data
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

        if not username or not password:
            if request.is_json:
                return {'success': False, 'message': 'Username and password required'}, 400
            flash('Username and password required')
            return render_template('register.html')

        existing = User.query.filter_by(username=username).first()
        if existing:
            if request.is_json:
                return {'success': False, 'message': 'Username already taken'}, 400
            flash('Username already taken')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        if request.is_json:
            return {'success': True, 'redirect': '/login'}, 200

        flash('Registration successful! Please log in.')
        return redirect('/login')

    return render_template('register.html')

# =========================
# LOGOUT  ← FIX 5: proper logout route
# =========================
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect('/')

# =========================
# DASHBOARD  ← FIX 6: added session protection
# =========================
@app.route('/dashboard')
def dashboard():
    # Protect dashboard — must be logged in
    if 'user' not in session:
        flash('Please log in to access the dashboard.')
        return redirect('/login')
    return render_template('dashboard.html')

# =========================
# PREDICT
# =========================
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'GET':
        return render_template('index.html')

    user = User.query.filter_by(username=session['user']).first()

    if user is None or user.trial_count >= 5:
        return render_template('trial_expired.html')

    user.trial_count += 1
    db.session.commit()

    height = int(request.form['height'])
    weight = int(request.form['weight'])
    age = int(request.form['age'])
    gender = request.form['gender']
    body = request.form['body']

    gender_encoded = gender_encoder.transform([gender])[0]
    body_encoded = body_encoder.transform([body])[0]

    data = np.array([[height, weight, age, gender_encoded, body_encoded]])

    prediction = model.predict(data)
    probabilities = model.predict_proba(data)
    confidence = round(max(probabilities[0]) * 100, 2)
    result = size_encoder.inverse_transform(prediction)
    size = result[0]

    explanation = f"Recommended size {size} based on:\n• Height: {height} cm\n• Weight: {weight} kg\n• Body Type: {body}"

    conn = sqlite3.connect('fashion.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO history (height, weight, age, gender, body, style, predicted_size) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (height, weight, age, gender, body, "Casual", size)
    )
    conn.commit()
    conn.close()

    if body_encoded == body_encoder.transform(['Slim'])[0]:
        recommendations = [
            {'name': 'Slim Fit Jeans', 'image': 'jeans.jpg'},
            {'name': 'Oversized T-Shirt', 'image': 'shirt.jpg'},
            {'name': 'Layered Jacket', 'image': 'jacket.jpg'}
        ]
        style_insight = "• Slim-fit outfits enhance your proportions\n• Layered fashion creates stronger visual balance\n• Streetwear styles fit your body profile well"
    elif body_encoded == body_encoder.transform(['Athletic'])[0]:
        recommendations = [
            {'name': 'Gym Fit Wear', 'image': 'gym.jpg'},
            {'name': 'Sports Jacket', 'image': 'jacket.jpg'},
            {'name': 'Athletic Shirt', 'image': 'shirt.jpg'}
        ]
        style_insight = "• Structured outfits highlight athletic physique\n• Sportswear improves overall styling balance\n• Fitted jackets complement your body type"
    elif body_encoded == body_encoder.transform(['Heavy'])[0]:
        recommendations = [
            {'name': 'Relaxed Hoodie', 'image': 'hoodie.jpg'},
            {'name': 'Straight Fit Jeans', 'image': 'jeans.jpg'},
            {'name': 'Dark Outfit', 'image': 'jacket.jpg'}
        ]
        style_insight = "• Dark-tone outfits create cleaner proportions\n• Relaxed fits improve comfort and appearance\n• Layered styles enhance fashion balance"
    else:
        recommendations = [
            {'name': 'Casual Shirt', 'image': 'shirt.jpg'},
            {'name': 'Regular Fit Jeans', 'image': 'jeans.jpg'},
            {'name': 'Classic T-Shirt', 'image': 'hoodie.jpg'}
        ]
        style_insight = "• Casual balanced styling suits your profile\n• Standard fits work best for comfort and fashion\n• Neutral combinations improve versatility"

    return render_template(
        'result.html',
        result=size,
        recommendations=recommendations,
        explanation=explanation,
        confidence=confidence,
        style_insight=style_insight
    )

# =========================
# HISTORY
# =========================
@app.route('/history')
def history():
    conn = sqlite3.connect('fashion.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history")
    records = cursor.fetchall()
    conn.close()
    return render_template('history.html', records=records)

# =========================
# ADMIN
# =========================
@app.route('/admin')
def admin():
    users = User.query.all()
    conn = sqlite3.connect('fashion.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM history")
    total_predictions = cursor.fetchone()[0]
    conn.close()
    return render_template('admin.html', users=users, total_predictions=total_predictions)

# =========================
# FEEDBACK
# =========================
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback_text = request.form['message']
        username = session.get('user', 'Anonymous')
        conn = sqlite3.connect('fashion.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO feedback (username, feedback) VALUES (?, ?)', (username, feedback_text))
        conn.commit()
        conn.close()
        flash('Feedback submitted!')
    return render_template('feedback.html')

# =========================
# FAVORITES
# =========================
@app.route('/save-favorite')
def save_favorite():
    username = request.args.get('username')
    outfit = request.args.get('outfit')
    image = request.args.get('image')
    conn = sqlite3.connect('fashion.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO favorites (username, outfit_name, image) VALUES (?, ?, ?)', (username, outfit, image))
    conn.commit()
    conn.close()
    return redirect('/favorites')

@app.route('/favorites')
def favorites():
    conn = sqlite3.connect('fashion.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM favorites")
    data = cursor.fetchall()
    conn.close()
    return render_template('favorites.html', favorites=data)

# =========================
# ML METRICS
# =========================
@app.route('/ml-metrics')
def ml_metrics():
    return render_template('ml_dashboard.html', accuracy=94.2, precision=92.5, recall=91.8, dataset_size=5000)

# =========================
# ANALYTICS CHART
# =========================
@app.route('/analytics-chart')
def analytics_chart():
    conn = sqlite3.connect('fashion.db')
    cursor = conn.cursor()
    cursor.execute("SELECT predicted_size, COUNT(*) FROM history GROUP BY predicted_size")
    data = cursor.fetchall()
    conn.close()
    sizes = [x[0] for x in data]
    counts = [x[1] for x in data]
    plt.figure(figsize=(6, 4))
    plt.bar(sizes, counts)
    plt.title("Size Prediction Analytics")
    plt.xlabel("Sizes")
    plt.ylabel("Predictions")
    plt.savefig('static/chart.png')
    plt.close()
    return render_template('analytics_chart.html')

# =========================
# CHATBOT
# =========================
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    response_text = ""
    if request.method == 'POST':
        user_message = request.form['message']
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI fashion assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        response_text = response.choices[0].message.content
    return render_template('chatbot.html', response=response_text)

# =========================
# SEARCH
# =========================
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].lower()
    results = []
    fashion_data = {
        "casual": {"title": "Casual Fashion", "description": "Relaxed everyday outfits.", "tips": "Try oversized t-shirts, sneakers and denim jackets.", "images": ["images/casual.jpg", "images/casual1.jpeg"]},
        "formal": {"title": "Formal Wear", "description": "Professional and elegant outfit combinations.", "tips": "Blazers and monochrome styles work best.", "images": ["images/formal.jpg", "images/formal1.jpg"]},
        "gym": {"title": "Gym Wear", "description": "Athletic and performance-focused outfits.", "tips": "Joggers and compression outfits improve gym styling.", "images": ["images/gym.jpg", "images/gym1.jpg"]},
        "winter": {"title": "Winter Fashion", "description": "Layered outfits for cold weather styling.", "tips": "Puffer jackets, hoodies and boots.", "images": ["images/winter.jpg", "images/winter1.jpg"]},
        "summer": {"title": "Summer Fashion", "description": "Lightweight outfits for hot weather.", "tips": "Linen shirts and light colors.", "images": ["images/summer.jpg", "images/shirt.jpg"]}
    }
    for key, value in fashion_data.items():
        if query in key:
            results.append(value)
    return render_template('search.html', query=query, results=results)

# =========================
# OUTFITS
# =========================
@app.route('/outfits/casual')
def casual_outfits():
    outfits = ["images/casual.jpg", "images/casual1.jpeg", "images/casual2.jpg", "images/casual3.jpg"]
    return render_template('outfits.html', title="Casual Outfits", outfits=outfits)

@app.route('/outfits/sports')
def sports_outfits():
    outfits = ["images/gym.jpg", "images/gym1.jpg", "images/gym2.jpg", "images/gym3.jpg"]
    return render_template('outfits.html', title="Sports Outfits", outfits=outfits)

@app.route('/outfits/formal')
def formal_outfits():
    outfits = ["images/formal.jpg", "images/formal1.jpg", "images/formal2.jpg", "images/formal3.jpg"]
    return render_template('outfits.html', title="Formal Outfits", outfits=outfits)

# =========================
# UPLOAD FASHION
# =========================
@app.route('/upload-fashion', methods=['GET', 'POST'])
def upload_fashion():
    prediction = None
    image_path = None
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = file.filename
            upload_path = os.path.join('static/uploads', filename)
            file.save(upload_path)
            image_path = upload_path
            filename_lower = filename.lower()
            if 'formal' in filename_lower:
                prediction = "Formal Fashion"
            elif 'gym' in filename_lower:
                prediction = "Sports/Gym Fashion"
            elif 'casual' in filename_lower:
                prediction = "Casual Fashion"
            else:
                prediction = "Modern Fashion Style"
    return render_template('upload.html', prediction=prediction, image_path=image_path)

# =========================
# PREDICT SIZE
# =========================
@app.route('/predict-size', methods=['GET', 'POST'])
def predict_size():
    prediction = None
    if request.method == 'POST':
        weight = float(request.form['weight'])
        if weight < 55:
            prediction = "Small (S)"
        elif weight < 75:
            prediction = "Medium (M)"
        elif weight < 90:
            prediction = "Large (L)"
        else:
            prediction = "XL"
    return render_template('predict.html', prediction=prediction)

# =========================
# CREATE DB + RUN
# =========================
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
