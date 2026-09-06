# =============================================================================
# app/blueprints/advanced.py  --  LEVEL 3 (ADVANCED) : the "hard" features
# =============================================================================
#   * File upload            : accept multipart, stream to disk
#   * Celery task trigger    : enqueue a background job, return fast
#   * Redis cache            : cache a slow computation
#   * Server-Sent Events     : push live updates over HTTP (real-time-ish)
#
# These mirror the FastAPI advanced router but with Flask's idioms, so you see
# the SAME concepts expressed in BOTH frameworks (a great interview contrast).

import os
import time
import uuid

import redis
from flask import Blueprint, current_app, jsonify, request, Response
from flask_login import current_user, login_required

from app.tasks import send_digest_email

bp = Blueprint("advanced", __name__, url_prefix="/api/advanced")

# Redis client (same container used by FastAPI too).
_redis = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"), decode_responses=True
)


# --- 1) FILE UPLOAD ------------------------------------------------------------
@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """Save an uploaded file to the local media folder.
       request.files['file'] gives a FileStorage object."""
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file provided"}), 422

    # only allow certain extensions (basic safety; production uses MIME checks)
    if not file.filename.lower().endswith((".txt", ".md", ".json")):
        return jsonify({"error": "File type not allowed"}), 415

    # media folder: created relative to the app root on the fly
    media_dir = os.path.join(current_app.root_path, "media")
    os.makedirs(media_dir, exist_ok=True)

    # unique-ish name to avoid collisions
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    file.save(os.path.join(media_dir, safe_name))        # streams to disk, not to RAM
    return jsonify({"saved_as": safe_name, "size": file.content_length})


# --- 2) CELERY BACKGROUND TASK ---------------------------------------------------
@bp.route("/digest", methods=["POST"])
@login_required
def trigger_digest():
    """Kick off a Celery task (a durable background job) and return fast.
       Compare with FastAPI BackgroundTasks: Celery survives restarts, retries,
       and can scale to many workers. Here we just .delay() and return an id."""
    # .delay queues the task on Redis; a real Celery worker would pick it up.
    task = send_digest_email.delay(current_user.email)
    return jsonify({"status": "queued", "task_id": task.id})


# --- 3) REDIS CACHE ----------------------------------------------------------------
@bp.route("/cached-time", methods=["GET"])
@login_required
def cached_time():
    """Cache an expensive result in Redis for 30s. 2nd call is instant.
       Note: we cache PER USER so different users don't share (and so we can
       invalidate per user later)."""
    key = f"user:{current_user.id}:cached_time"
    cached = _redis.get(key)
    if cached:
        return jsonify({"source": "cache", "data": cached})
    time.sleep(3)                              # pretend slow work
    value = f"computed@{time.time():.0f}"
    _redis.setex(key, 30, value)               # TTL 30s
    return jsonify({"source": "fresh", "data": value})


# --- 4) SERVER-SENT EVENTS (real-time push) --------------------------------------
# SSE: the server keeps the HTTP response OPEN and pushes lines as they happen.
# Client reads them live (no polling). A lighter alternative to WebSockets.
@bp.route("/events", methods=["GET"])
def stream_events():
    def generate():
        for i in range(5):
            yield f"data: tick {i}\n\n"        # each "data: ...\n\n" is one message
            time.sleep(1)
    # mimetype text/event-stream tells clients to stream it.
    return Response(generate(), mimetype="text/event-stream")
