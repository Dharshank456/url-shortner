import sqlite3
import os

# store DB in a guaranteed writable location
DB_DIR = "/tmp"
DB_PATH = os.path.join(DB_DIR, "urls.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
