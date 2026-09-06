# =============================================================================
# tests/test_basic_auth.py  --  basic routes + authentication flow
# =============================================================================

import pytest


def test_hello(client):
    resp = client.get("/api/basic/hello")
    assert resp.status_code == 200
    assert resp.json["message"] == "Hello, world!"


def test_basic_crud(client):
    # create
    created = client.post("/api/basic/items", json={"name": "pen", "price": 1.5})
    assert created.status_code == 201
    item_id = created.json["id"]

    # read
    got = client.get(f"/api/basic/items/{item_id}")
    assert got.status_code == 200
    assert got.json["name"] == "pen"

    # list
    listed = client.get("/api/basic/items")
    assert listed.status_code == 200
    assert listed.json["total"] >= 1

    # delete -> 204 with no body
    deleted = client.delete(f"/api/basic/items/{item_id}")
    assert deleted.status_code == 204

    # now 404
    assert client.get(f"/api/basic/items/{item_id}").status_code == 404


def test_basic_validation(client):
    # missing required `name` -> 422
    resp = client.post("/api/basic/items", json={"price": 2})
    assert resp.status_code == 422


# ---- auth flow ---------------------------------------------------------------
def test_register_then_login(client):
    # register
    reg = client.post("/api/auth/register", json={"email": "a@b.com", "password": "secret123"})
    assert reg.status_code == 201

    # duplicate -> 409
    dup = client.post("/api/auth/register", json={"email": "a@b.com", "password": "secret123"})
    assert dup.status_code == 409

    # login
    login = client.post("/api/auth/login", json={"email": "a@b.com", "password": "secret123"})
    assert login.status_code == 200

    # wrong password -> 401
    bad = client.post("/api/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert bad.status_code == 401


def test_me_requires_login(client):
    # no session -> 401 (login_required + unauthorized_handler returns JSON)
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_full_login_logout(client):
    client.post("/api/auth/register", json={"email": "c@d.com", "password": "secret123"})
    client.post("/api/auth/login", json={"email": "c@d.com", "password": "secret123"})
    me = client.get("/api/auth/me")       # session cookie now present
    assert me.status_code == 200
    assert me.json["email"] == "c@d.com"

    out = client.post("/api/auth/logout")
    assert out.status_code == 200
    # after logout the session is gone -> 401 again
    assert client.get("/api/auth/me").status_code == 401
