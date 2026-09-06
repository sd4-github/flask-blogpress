# =============================================================================
# tests/conftest.py  --  pytest fixtures for the Flask project
# =============================================================================
# Key Flask testing patterns (interview):
#   * create_app(TestConfig) -> app pointed at the isolated test DB.
#   * app.test_client()      -> an HTTP client that runs the full stack.
#   * app.app_context()      -> some Flask features need the app context to be
#     active (e.g. db session resolution). The test client pushes it for you,
#     but CLI/scripts sometimes need it explicitly.
#   * drop_all/create_all per test = clean, deterministic database per test
#     (here done at session scope + a per-test purge for extra isolation).

import os

# Point config at the test DB BEFORE importing the app.
os.environ.setdefault(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://blogpress:blogpress@127.0.0.1:5432/blogpress_test",
)

import pytest  # noqa: E402

from app import create_app  # noqa: E402
from app.config import TestConfig  # noqa: E402
from app.extensions import db  # noqa: E402


@pytest.fixture()
def app():
    """Build a fresh app wired to the test database."""
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()      # start clean
        db.create_all()    # create all tables
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """HTTP test client for end-to-end requests."""
    return app.test_client()


@pytest.fixture()
def app_ctx(app):
    """Expose the app instance for direct db.session manipulation.
       NOTE: we deliberately do NOT keep an app context pushed for the whole
       test. Holding one open makes Flask-Login's `current_user` and SQLAlchemy
       reuse a single long-lived session across requests, which causes stale /
       detached-instance bugs. The helper functions open their own short-lived
       `with app.app_context():` blocks instead."""
    return app
