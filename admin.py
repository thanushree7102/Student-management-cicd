"""M3 - Admin module (Flask Blueprint).

Owns only the /admin/... pages. It does not create the students table and does not
render any page from other modules. To plug it into the main app, add:

    from admin import admin_bp, init_admin_table
    app.register_blueprint(admin_bp)
    with app.app_context():
        init_admin_table()      # creates the admins table + first admin (once)

The app must set app.secret_key. Database access is isolated in get_db() so it
can be pointed at the AWS database later.
"""
import csv, io, os, secrets, sqlite3
from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash, abort, Response, current_app)
from werkzeug.security import check_password_hash, generate_password_hash

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------- database (the only place to change for AWS) ----------------
def get_db():
    path = current_app.config.get("DATABASE") or os.path.join(
        os.environ.get("DB_DIR", "data"), "students.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_admin_table():
    """Create the admins table and seed the first admin from ADMIN_USER / ADMIN_PASSWORD."""
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL)""")
    if conn.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
        conn.execute("INSERT INTO admins(username, password_hash) VALUES(?,?)",
                     (os.environ.get("ADMIN_USER", "admin"),
                      generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123"))))
    conn.commit()
    conn.close()


# ---------------- security: CSRF + login guard for every /admin route ----------------
def _csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


@admin_bp.context_processor
def _inject():
    return {"csrf_token": _csrf_token}


@admin_bp.before_request
def _guard():
    if request.method == "POST" and request.form.get("csrf_token") != session.get("csrf"):
        abort(400, "Invalid CSRF token")
    if request.endpoint != "admin.login" and not session.get("admin"):
        flash("Please log in as admin.", "error")
        return redirect(url_for("admin.login"))


# ---------------- auth ----------------
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        row = conn.execute("SELECT * FROM admins WHERE username=?",
                           (request.form.get("username", "").strip(),)).fetchone()
        conn.close()
        if row and check_password_hash(row["password_hash"], request.form.get("password", "")):
            session.clear()
            session["admin"] = row["username"]
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("admin/login.html")


@admin_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("admin.login"))


# ---------------- dashboard ----------------
@admin_bp.route("/")
def dashboard():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    depts = conn.execute(
        "SELECT dept, COUNT(*) AS n FROM students GROUP BY dept ORDER BY n DESC").fetchall()
    latest = conn.execute(
        "SELECT id,name,usn,dept FROM students ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    top = max([d["n"] for d in depts], default=1)
    return render_template("admin/dashboard.html", total=total, depts=depts,
                           latest=latest, top=top)


# ---------------- student management ----------------
@admin_bp.route("/students")
def students():
    q = request.args.get("q", "").strip()
    conn = get_db()
    if q:
        like = f"%{q}%"
        rows = conn.execute(
            "SELECT id,name,usn,dept FROM students "
            "WHERE name LIKE ? OR usn LIKE ? OR dept LIKE ? ORDER BY id DESC",
            (like, like, like)).fetchall()
    else:
        rows = conn.execute("SELECT id,name,usn,dept FROM students ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin/students.html", students=rows, q=q)


@admin_bp.route("/students/<int:sid>/edit", methods=["GET", "POST"])
def edit(sid):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    if not student:
        conn.close()
        abort(404)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        usn = request.form.get("usn", "").strip().upper()
        dept = request.form.get("dept", "").strip()
        clash = conn.execute("SELECT 1 FROM students WHERE usn=? AND id!=?", (usn, sid)).fetchone()
        if not (name and usn and dept):
            flash("All fields are required.", "error")
        elif clash:
            flash(f"USN {usn} belongs to another student.", "error")
        else:
            conn.execute("UPDATE students SET name=?, usn=?, dept=? WHERE id=?",
                         (name, usn, dept, sid))
            conn.commit()
            conn.close()
            flash("Student updated.", "success")
            return redirect(url_for("admin.students"))
        student = {"id": sid, "name": name, "usn": usn, "dept": dept}
    conn.close()
    return render_template("admin/edit.html", s=student)


@admin_bp.route("/students/<int:sid>/delete", methods=["POST"])
def delete(sid):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    flash("Student deleted.", "success")
    return redirect(url_for("admin.students"))


@admin_bp.route("/export")
def export():
    conn = get_db()
    rows = conn.execute("SELECT id,name,usn,dept FROM students ORDER BY id").fetchall()
    conn.close()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ID", "Name", "USN", "Department"])
    for r in rows:  # prefix risky cells so Excel does not run them as formulas
        w.writerow([r["id"]] + [("'" + c if str(c)[:1] in "=+-@" else c)
                                for c in (r["name"], r["usn"], r["dept"])])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=students.csv"})


@admin_bp.route("/password", methods=["GET", "POST"])
def password():
    if request.method == "POST":
        old, new = request.form.get("old", ""), request.form.get("new", "")
        conn = get_db()
        row = conn.execute("SELECT * FROM admins WHERE username=?", (session["admin"],)).fetchone()
        if not check_password_hash(row["password_hash"], old):
            flash("Current password is wrong.", "error")
        elif len(new) < 8:
            flash("New password must be at least 8 characters.", "error")
        else:
            conn.execute("UPDATE admins SET password_hash=? WHERE id=?",
                         (generate_password_hash(new), row["id"]))
            conn.commit()
            flash("Password changed.", "success")
        conn.close()
    return render_template("admin/password.html")
