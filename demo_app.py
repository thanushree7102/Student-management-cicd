"""Local demo/test harness ONLY. The real app.py belongs to the integrator.
Run:  python demo_app.py   then open http://localhost:5000/admin/login
"""
import os, sqlite3
from flask import Flask, redirect
from admin import admin_bp, init_admin_table

HERE = os.path.dirname(os.path.abspath(__file__))


def create_app(db_path=None):
    app = Flask(__name__, template_folder=os.path.join(HERE, "templates"),
                static_folder=os.path.join(HERE, "static"))
    app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config["DATABASE"] = db_path or os.path.join(HERE, "demo.db")
    conn = sqlite3.connect(app.config["DATABASE"])   # stand-in for the shared students table
    conn.execute("""CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, usn TEXT NOT NULL, dept TEXT NOT NULL)""")
    conn.commit(); conn.close()
    app.register_blueprint(admin_bp)
    with app.app_context():
        init_admin_table()
    app.add_url_rule("/", "home", lambda: redirect("/admin/"))
    return app


if __name__ == "__main__":
    create_app().run(port=5000)
