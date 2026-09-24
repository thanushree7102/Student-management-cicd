import os, sqlite3, sys, tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from demo_app import create_app  # noqa: E402


@pytest.fixture
def client():
    db = os.path.join(tempfile.mkdtemp(), "t.db")
    app = create_app(db)
    app.config["TESTING"] = True
    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO students(name,usn,dept) VALUES('Asha','1VU23CS001','CSE')")
    conn.commit(); conn.close()
    with app.test_client() as c:
        with c.session_transaction() as s:
            s["csrf"] = "tok"
        yield c


def post(c, url, **data):
    data["csrf_token"] = "tok"
    return c.post(url, data=data, follow_redirects=True)


def login(c):
    r = post(c, "/admin/login", username="admin", password="admin123")
    with c.session_transaction() as s:      # login rotates the session
        s["csrf"] = "tok"
    return r


def test_requires_login(client):
    r = client.get("/admin/")
    assert r.status_code == 302 and "/admin/login" in r.headers["Location"]


def test_bad_login(client):
    assert b"Invalid username or password" in post(client, "/admin/login", username="admin", password="x").data


def test_dashboard_and_search(client):
    login(client)
    assert b"Total Students" in client.get("/admin/").data
    assert b"Asha" in client.get("/admin/students?q=asha").data
    assert b"Asha" not in client.get("/admin/students?q=zzz").data


def test_edit_delete_export(client):
    login(client)
    post(client, "/admin/students/1/edit", name="Asha K", usn="1vu23cs001", dept="ECE")
    assert b"Asha K" in client.get("/admin/students").data
    assert b"1VU23CS001" in client.get("/admin/export").data
    post(client, "/admin/students/1/delete")
    assert b"Asha K" not in client.get("/admin/students").data


def test_change_password(client):
    login(client)
    assert b"at least 8" in post(client, "/admin/password", old="admin123", new="short").data
    assert b"Password changed" in post(client, "/admin/password", old="admin123", new="newpass123").data


def test_csrf_blocked(client):
    assert client.post("/admin/login", data={"username": "a", "password": "b"}).status_code == 400
