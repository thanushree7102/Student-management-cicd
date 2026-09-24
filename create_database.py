import sqlite3
import os
from werkzeug.security import generate_password_hash


DB_DIR = os.environ.get("DB_DIR", "data")
DB_PATH = os.path.join(DB_DIR, "students.db")


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            usn TEXT NOT NULL UNIQUE,
            date_of_birth TEXT,
            gender TEXT,
            department TEXT NOT NULL,
            semester TEXT,
            section TEXT,
            admission_year TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            parent_name TEXT,
            parent_phone TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    if cur.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
        user = os.environ.get("ADMIN_USER", "admin")
        pwd = os.environ.get("ADMIN_PASSWORD", "admin123")

        cur.execute(
            "INSERT INTO admins(username, password_hash) VALUES(?, ?)",
            (user, generate_password_hash(pwd))
        )

    conn.commit()
    conn.close()

    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()