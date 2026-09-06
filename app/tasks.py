# =============================================================================
# app/tasks.py  --  Celery: durable background tasks
# =============================================================================
# Same idea as the FastAPI celery_app.py: enqueue work on Redis, and one or
# more Celery workers process it asynchronously — durable, retry-able, scalable.
#
# RUN A WORKER:
#   .venv/bin/celery -A app.tasks.celery_app worker --loglevel=info

import os
import time

from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

# broker = where tasks queue; backend = where results are stored.
celery_app = Celery("blogpress", broker=redis_url, backend=redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,   # quiet a deprecation warning
)


@celery_app.task(name="send_digest_email")
def send_digest_email(user_email: str) -> dict:
    """A simulated long-running background job. In prod: SMTP, PDF, ETL..."""
    print(f"[celery] sending digest to {user_email}")
    time.sleep(3)                              # pretend work happens here
    return {"email": user_email, "status": "sent"}
