"""Test setup: a tiny Flask app that mounts the admin Blueprint on a temp database.
The real app.py belongs to the integrator, so tests do not depend on it."""
import os, sqlite3, sys, tempfile
import pytest
from flask import Flask

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from admin import admin_bp, init_admin_table  # noqa: E402


@pytest.fixture
def client():
    db = os.path.join(tempfile.mkdtemp(), "test.db")
    app = Flask(__name__, template_folder=os.path.join(ROOT, "templates"),
                static_folder=os.path.join(ROOT, "static"))
    app.secret_key = "test-key"
    app.config.update(DATABASE=db, TESTING=True)
    conn = sqlite3.connect(db)   # stand-in for the shared students table
    conn.execute("""CREATE TABLE students (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, usn TEXT NOT NULL, dept TEXT NOT NULL)""")
    conn.execute("INSERT INTO students(name,usn,dept) VALUES('Asha','1VU23CS001','CSE')")
    conn.commit(); conn.close()
    app.register_blueprint(admin_bp)
    with app.app_context():
        init_admin_table()
    with app.test_client() as c:
        with c.session_transaction() as s:
            s["csrf"] = "tok"
        yield c
