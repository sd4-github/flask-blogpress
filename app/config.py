# =============================================================================
# app/config.py  --  Flask configuration classes
# =============================================================================
# Best practice: separate config classes per environment so the same app can
# run in dev / test / production just by flipping which class is loaded.
# `create_app(ConfigClass)` picks one (see app/__init__.py).
#
# KEY CONCEPTS (interview):
#   * SQLALCHEMY_DATABASE_URI  -> which DB SQLAlchemy uses.
#   * SECRET_KEY               -> signs Flask session cookies (server-side
#     session auth, unlike FastAPI's JWT). NEVER commit a real one.
#   * `TestConfig` uses a SEPARATE test DB and disables CSRF so tests run clean.

import os


class Config:
    """Base config — defaults for all environments."""
    # Secret key that signs the client's session cookie.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://blogpress:blogpress@127.0.0.1:5432/blogpress",
    )
    # Flask 3: tracks_database_modifications is noisy — always disable.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # WTF / CSRF
    WTF_CSRF_ENABLED = True          # protect against cross-site requests

    # For pure-backend JSON APIs, lifetime of the token header used by tests.
    JSON_SORT_KEYS = False           # keep JSON output field order as defined


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestConfig(Config):
    """Isolated DB + CSRF off for fast, clean unit tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg2://blogpress:blogpress@127.0.0.1:5432/blogpress_test",
    )
    WTF_CSRF_ENABLED = False         # tests can hit true JSON endpoints easily
