import os
import sqlite3
import datetime
import json
from flask import Flask, render_template, request, redirect, url_for, session

DB_PATH = os.environ.get('DB_PATH', 'submissions.db')
SETTINGS_PATH = os.environ.get('SETTINGS_PATH', 'settings.json')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme')

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev')


def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            destination TEXT,
            travel_date TEXT,
            budget TEXT,
            image_urls TEXT,
            message TEXT,
            created_at TEXT
        )
    ''')
    c.execute('PRAGMA table_info(submissions)')
    columns = {row[1] for row in c.fetchall()}
    if 'image_urls' not in columns:
        c.execute('ALTER TABLE submissions ADD COLUMN image_urls TEXT')
    conn.commit()
    conn.close()


init_db()

DEFAULT_SETTINGS = {
    'hero_heading': 'Plan your next adventure',
    'hero_subheading': 'Tell us a bit about your travel plans and we’ll get back with a personalized quote.',
    'feature_list': [
        'Personalized itineraries',
        'Theme park magic & character moments',
        'Resort, cruise, and dining coordination',
    ],
    'whimsy_title': 'Whimsy touches we love',
    'whimsy_body': 'Pixie-dusted planning, surprise celebrations, and storybook details that make every day feel enchanted.',
    'whimsy_tags': [
        'Park strategy',
        'Princess-worthy stays',
        'Firework nights',
    ],
    'gallery_images': [],
}


def load_settings():
    settings = DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
            if isinstance(data, dict):
                settings.update({key: value for key, value in data.items() if value is not None})
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass
    return settings


def save_settings(settings):
    settings_dir = os.path.dirname(SETTINGS_PATH)
    if settings_dir:
        os.makedirs(settings_dir, exist_ok=True)
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as handle:
        json.dump(settings, handle, indent=2)


@app.route('/', methods=['GET'])
def index():
    settings = load_settings()
    return render_template('index.html', settings=settings)


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    destination = request.form.get('destination', '').strip()
    travel_date = request.form.get('travel_date', '').strip()
    budget = request.form.get('budget', '').strip()
    message = request.form.get('message', '').strip()
    created_at = datetime.datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO submissions (name, email, phone, destination, travel_date, budget, image_urls, message, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, email, phone, destination, travel_date, budget, '', message, created_at))
    conn.commit()
    conn.close()

    return render_template('thanks.html', name=name)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('is_admin'):
        return render_template('admin_login.html')

    settings = load_settings()
    if request.method == 'POST':
        feature_list = [
            item.strip()
            for item in request.form.get('feature_list', '').splitlines()
            if item.strip()
        ]
        whimsy_tags = [
            tag.strip()
            for tag in request.form.get('whimsy_tags', '').splitlines()
            if tag.strip()
        ]
        gallery_images = [
            url.strip()
            for url in request.form.get('gallery_images', '').splitlines()
            if url.strip()
        ]
        settings.update({
            'hero_heading': request.form.get('hero_heading', '').strip(),
            'hero_subheading': request.form.get('hero_subheading', '').strip(),
            'feature_list': feature_list,
            'whimsy_title': request.form.get('whimsy_title', '').strip(),
            'whimsy_body': request.form.get('whimsy_body', '').strip(),
            'whimsy_tags': whimsy_tags,
            'gallery_images': gallery_images,
        })
        save_settings(settings)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM submissions ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return render_template('admin.html', submissions=rows, settings=settings)


@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['is_admin'] = True
        return redirect(url_for('admin'))
    return render_template('admin_login.html', error='Invalid credentials')


@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
