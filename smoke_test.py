#!/usr/bin/env python3
"""
smoke_test.py  --  verify the ADVANCED features end-to-end (in-process).

Usage:  /home/soumikd4/Desktop/code/interview-prep/2_flask_blogpress/.venv/bin/python smoke_test.py
"""
import os
import time

from app import create_app
from app.config import DevelopmentConfig
from app.extensions import db

app = create_app(DevelopmentConfig)
with app.app_context():
    db.create_all()

c = app.test_client()

# --- register + login -------------------------------------------------------
email = "smoke@example.com"
c.post("/api/auth/register", json={"email": email, "password": "secret123"})
login = c.post("/api/auth/login", json={"email": email, "password": "secret123"})
assert login.status_code == 200, login.get_json()
print("[ok] logged in")
assert c.get("/api/auth/me").status_code == 200

# --- upload -----------------------------------------------------------------
import io
data = {"file": (io.BytesIO(b"hello"), "notes.txt")}
up = c.post("/api/advanced/upload", data=data, content_type="multipart/form-data")
assert up.status_code == 200, up.get_json()
print("[ok] upload:", up.get_json())

# --- redis cache (fresh then cached) -----------------------------------------
t0 = time.time()
r1 = c.get("/api/advanced/cached-time")
fresh = time.time() - t0
assert r1.get_json()["source"] == "fresh"
t0 = time.time()
r2 = c.get("/api/advanced/cached-time")
cached = time.time() - t0
assert r2.get_json()["source"] == "cache"
print(f"[ok] redis cache: fresh={fresh:.2f}s cached={cached:.3f}s")

# --- celery digest (enqueue; worker not required to get a task id) ------------
dg = c.post("/api/advanced/digest")
assert dg.status_code == 200
print("[ok] celery task queued:", dg.get_json())

# --- SSE streaming (read a couple of lines) -----------------------------------
resp = c.get("/api/advanced/events", buffered=True)
assert resp.status_code == 200
assert "tick" in resp.get_data(as_text=True)
print("[ok] SSE streamed data")

print("\nALL FLASK SMOKE TESTS PASSED")
