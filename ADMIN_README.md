# M3 - Admin Module

Owner: Thanushree (Admin). Files owned by this module only:
`admin.py`, `templates/admin/`, `static/admin.css`, `static/admin.js`, `tests/test_admin.py`
(`demo_app.py` is a local test harness, not part of the real app).

## Integration (2 lines in the main app.py)
```python
from admin import admin_bp, init_admin_table
app.register_blueprint(admin_bp)
with app.app_context():
    init_admin_table()   # creates `admins` table + first admin
```
Requirements: `app.secret_key` set (env SECRET_KEY), Flask (Werkzeug comes with it).

## Database contract
- Reads/writes the shared `students(id, name, usn, dept)` table (created by the DB owner).
- Creates only its own `admins(id, username, password_hash)` table.
- All DB access is in `get_db()` in admin.py - change it there if the AWS database is not SQLite.

## Env vars
`SECRET_KEY`, `ADMIN_USER`, `ADMIN_PASSWORD` (first admin, used only when `admins` is empty).

## Routes
/admin/login, /admin/logout, /admin/ (dashboard), /admin/students (search),
/admin/students/<id>/edit, /admin/students/<id>/delete, /admin/export, /admin/password
