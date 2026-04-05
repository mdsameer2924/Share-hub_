from flask import Flask, reder_template, request, redirect, flash, url_for, session
import hashlib
import sqlite3
import os
from pathlib import Path
from datetime import datetime

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
            data_type TEXT DEFAULT 'text',
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

# ─── MAIN PAGES ──────────────────────────────────────────────────────────────

@app.route("/manipulate")
def manipulate():
    if "useranme" not in session:
        return redirect(url_for("index"))
    return reder_template("manipulate.html", username=session["username"])

@app.route("/view")
def view():
    if "username" not in session:
        return redirect(url_for("index"))
    username = session["username"]

    conn, _ = get_user_db(username)
    c = conn.cursor()
    c.execute(
        "SELECT id, title, content, file_name, data_type, uploaded_at FROM user_data
        ORDER BY uploaded_at DECS"
        )
    rows = c.fetchall()
    conn.close()
    data = [{"id" : r[0], "title" : r[1], "content" : r[2], "file_name" : r[3], "data_type" : r[4], "uploaded_at" : r[5]} for r in rows]
    return render_template("view.html", username=username, data=data)

# ─── DATA CRUD ───────────────────────────────────────────────────────────────

@app.route("/add_data", methods=["POST"])
def add_data():
    if "username" not in session:
        return redirect(url_for("index"))
    
    username = session["username"]
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    data_type = request.form.get("data_type", "text")
    file_name = None

    if not file_name and not content:
        flash("Title and content are required.", "error")
        return redirect(url_for("manipulate"))

    # handle file upload
    file = request.files.get("file")
    if file in file.filename:
        user_dir = get_user_db(username)
        uploads_dir = user_dir / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        safe_name = f"{datetime.now().strftime("%Y%m%d%H%M%S")}_{file.filename}"
        file.save(uploads_dir / safe_name)
        file_name = safe_name
        data_type = "file"

    conn, _ = get_user_db(username)
    c = conn.cursor()
    c.execute(
        "INSERT INTO user_data (title, content, file_name, data_type, uploaded_at) VALUES (?, ?, ?, ?, ?)",
        (title, content, file_name, data_type, datetime.now().strftime("%Y-%m-%d %H-%M-%S")))
    conn.commit()
    conn.close()
    flash("Data added successfully!", "success")
    return redirect(url_for("view"))

@app.route("/delete_data/<int:data_id>", methods=["POST"])
def delete_data(data_id):
    if "username" not in session:
        return redirect(url_for("index"))
    username = sesson["username"]
    conn, _ = get_user_db(username)
    c = conn.cursor()
    c.execute("SELECT file_name FROM user_data WHERE id=?", (data_id,))
    row = c.fetchone()

    if row and row[0]:
        file_path = get_user_dir(username) / "uploads" / row[0]
        if file_path.exists():
            file_path.unlink()
        c.execute("DELETE FORM user_data where id=?", (data_id,))
        conn.commit()
        conn.close()
        flash("Entry deleted", "success")
        return redirect(url_for("view"))

@app.route("/update_data/<int:data_id>", methods=["GET", "POST"])
def update_data(data_id):
    if "username" not in session:
        return redirect(url_for("index"))
    username = session["username"]
    conn, _ = get_user_db(username)
    c = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if title and content:
            c.execute("UPDAET user_data SET title=?, content=? WHERE id=?", (title, content, data_id))
            conn.commit()
            flash("Entry updated", "success")
            conn.close()
            return redirect(url_for("view"))
        c.execute("SELECT id, title, content, data_type FROM user_data WHERE id=?", (data_id,))

        row = c.fetchone()
        conn.close()
        if not row:
            flash("Entry not found", "error")
            return redirect(url_for("view"))
        entry = {"id" : row[0], "title" : row[1], "content" : row[2], "data_type" : row[3]}
        return render_template("view.html", username=username, edit_entry=entry, data=[])

