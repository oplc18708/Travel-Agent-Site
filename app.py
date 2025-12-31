import os
import sqlite3
import datetime
from flask import Flask, render_template, request, abort

DB_PATH = os.environ.get('DB_PATH', 'submissions.db')
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'changeme')

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


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    destination = request.form.get('destination', '').strip()
    travel_date = request.form.get('travel_date', '').strip()
    budget = request.form.get('budget', '').strip()
    image_urls = [
        url.strip()
        for url in request.form.getlist('image_urls')
        if url.strip()
    ]
    image_urls_text = '\n'.join(image_urls)
    message = request.form.get('message', '').strip()
    created_at = datetime.datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO submissions (name, email, phone, destination, travel_date, budget, image_urls, message, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, email, phone, destination, travel_date, budget, image_urls_text, message, created_at))
    conn.commit()
    conn.close()

    return render_template('thanks.html', name=name)


@app.route('/admin', methods=['GET'])
def admin():
    key = request.args.get('key', '')
    if key != ADMIN_KEY:
        abort(401)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM submissions ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return render_template('submissions.html', submissions=rows)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
