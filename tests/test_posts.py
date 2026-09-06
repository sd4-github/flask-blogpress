# =============================================================================
# tests/test_posts.py  --  posts REST API (roles + ownership)
# =============================================================================

import pytest

from app.extensions import db
from app.models import User


def _register_login(client, email, role="reader", app_ctx=None):
    """Register a user, log them in, and (optionally) promote their role
       directly in the DB (since the register endpoint deliberately never
       lets clients choose their own role)."""
    client.post("/api/auth/register", json={"email": email, "password": "secret123"})
    client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    if role != "reader":
        with app_ctx.app_context():
            db.session.remove()            # start with a fresh, empty session
            u = User.query.filter_by(email=email).first()
            u.role = role
            db.session.commit()
            db.session.remove()            # release it so requests see fresh data
    return client


def test_posts_require_auth_to_create(client):
    # anonymous -> 401 (login_required)
    resp = client.post("/api/posts", json={"title": "t", "body": "b"})
    assert resp.status_code == 401


def test_reader_cannot_create(client):
    # registered but role=reader -> 403 (forbidden, not just unauth)
    _register_login(client, "reader@x.com", role="reader")
    resp = client.post("/api/posts", json={"title": "t", "body": "b"})
    assert resp.status_code == 403


def test_author_crud_and_ownership(client, app_ctx):
    _register_login(client, "writer@y.com", role="author", app_ctx=app_ctx)

    # author creates a post
    created = client.post("/api/posts", json={"title": "My first post", "body": "hello"})
    assert created.status_code == 201
    post_id = created.json["id"]

    # a draft is NOT visible publicly
    anon = app_ctx.test_client()
    assert anon.get(f"/api/posts/{post_id}").status_code == 404

    # author can publish it
    pub = client.patch(f"/api/posts/{post_id}", json={"published": True})
    assert pub.status_code == 200
    assert pub.json["published"] is True

    # now a different author cannot edit it (403)
    _register_login(client, "intruder@x.com", role="author", app_ctx=app_ctx)
    intruder = client.patch(f"/api/posts/{post_id}", json={"title": "hijack"})
    assert intruder.status_code == 403


def test_admin_can_edit_any_post(client, app_ctx):
    # create as author
    _register_login(client, "author@a.com", role="author", app_ctx=app_ctx)
    created = client.post("/api/posts", json={"title": "t", "body": "b"})
    assert created.status_code == 201
    pid = created.json["id"]

    # separate admin client edits it
    admin_client = _register_login(client, "admin@a.com", role="admin", app_ctx=app_ctx)
    resp = admin_client.patch(f"/api/posts/{pid}", json={"body": "edited by admin"})
    assert resp.status_code == 200
    assert resp.json["body"] == "edited by admin"


def test_pagination(client, app_ctx):
    # author publishes 3 posts
    _register_login(client, "pager@x.com", role="author", app_ctx=app_ctx)
    for i in range(3):
        client.post("/api/posts", json={"title": f"p{i}", "body": "x", "published": True})

    # paginated list returns all 3 total, 2 per page
    resp = client.get("/api/posts?page=1&per_page=2")
    assert resp.status_code == 200
    body = resp.json
    assert body["total"] == 3
    assert len(body["items"]) == 2
