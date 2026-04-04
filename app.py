from flask import Flask
import hashlib
import sqlite3

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


