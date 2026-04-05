from flask import Flask, reder_template, request, redirect, flash, url_for, session
import hashlib
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "sharehub_secret_key_2026"

USERS_ROOT = "user_directories"
MASTER_DB = "sharehub_master.db"

# ─── MASTER DB SETUP ─────────────────────────────────────────────────────────

def init_master_db():
    conn = sqlite3.connect(USERS_ROOT)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            cretaed_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── USER DB SETUP ───────────────────────────────────────────────────────────

def get_user_dir(username):
    path = Path(USERS_ROOT) / f"{username}_directory"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_user_db(username):
    user_dir = get_user_dir(username)
    db_path = user_dir / "data.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users_data(
            id INTEGER PRIMAY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            file_name TEXT,
            datatype TEXT DEFAULT 'text',
            uploaded_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    return conn, str(db_path)

# ─── AUTH ROUTES ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("manipulate"))
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "").strip()
    
    if not username or not password:
        flash("username and password required", "error")
        return redirect(url_for("index"))

    if len(useranme) < 3:
        flash("useraname must be at least 3 three characters.", "error")
        return redirect(url_for("index"))

    conn = sqlite3.connect(MASTER_DB)
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users(username, password, created_at) VALUES (?, ?, ?)",
            (username, hash_password(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        get_user_dir(username) # create user directory
        get_user_db(username) # initialize user database
        flash("Account created, please log in.", "success")
    except sqlite3.IntegretyError:
        flash("Username already taken.", "error")
    finally:
        conn.close()
    return redirect(url_for("index"))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "").strip()

    conn = sqlite3.connect(MASTER_DB)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=? AND password=?",
            username, hash_password(password))
    user = c.fetchone()
    conn.close()
    if user:
        session['username'] = username
        return redirect(url_for("manipulate"))
    else:
        flash("Invalid crediantials.", "error")
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("useranme", None)
    return redirect(url_for("index"))


