from flask import Flask
import hashlib
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "sharehub_secret_key_2026"

USERS_ROOT = "user_directories"
MASTER_DB = "sharehub_master.db"

# ─── MASTER DB SETUP ─────────────────────────────────────────────────────────

def init_master_db():
    with sqlite3.connect(USERS_ROOT) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                cretaed_at TEXT NOT NULL
            )
        """)

        conn.commit()

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
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users_data(
                id INTEGER PRIMAY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                file_name TEXT,                                                                              datatype TEXT DEFAULT 'text',
                 uploaded_at TEXT NOT NULL
            )
        """)
        conn.commit()


