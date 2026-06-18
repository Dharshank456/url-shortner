import sqlite3

DATABASE = "urls.db"


def get_connection():
    return sqlite3.connect(DATABASE)


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
