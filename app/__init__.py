# =============================================================================
# app/__init__.py  --  the "app factory"
# =============================================================================
# WHY A FACTORY? (industry-standard + interview question)
#   create_app() builds a NEW app each call. Benefits:
#     * Tests create a fresh app with a fresh test DB per test.
#     * Multiple app instances (dev/prod) share the same code.
#     * No module-level global app = fewer circular imports.
#
# We do three things here: configure, register extensions, register blueprints.

from flask import Flask, jsonify
from flask_login import LoginManager

from app.config import Config
from app.extensions import db, login_manager, migrate
from app.models import User


def create_app(config_class=Config):
    # --- 1) build + configure the app ------------------------------------
    app = Flask(__name__)
    app.config.from_object(config_class)      # load settings from config.py

    # --- 2) bind extensions to this app ----------------------------------
    db.init_app(app)                          # SQLAlchemy
    migrate.init_app(app, db)                 # migrations
    login_manager.init_app(app)               # session auth

    # Flask-Login needs a way to load a User from its session id.
    # Callback registered via the user_loader decorator (module-level below).
    login_manager.init_app(app)

    # What happens when login_required blocks an unauthenticated JSON request.
    login_manager.unauthorized_handler = unauthorized

    # --- 3) register blueprints (modular routable modules) ----------------
    from app.blueprints import advanced, auth, basic, posts
    app.register_blueprint(basic.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(advanced.bp)

    # --- 4) global error handlers ------------------------------------------
    register_error_handlers(app)

    # --- 5) CLI commands ----------------------------------------------------
    from app.cli import register_commands
    register_commands(app)

    # --- 6) create tables if missing (dev convenience; use migrations in prod)
    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id: str):
    """Flask-Login: turn a session's user id into a User (or None).
       Registering via the decorator tells Flask-Login how to load a user
       from the id stored in the session cookie."""
    return db.session.get(User, int(user_id))


def unauthorized():
    """Return JSON (not HTML) so a pure-backend client gets a clean 401."""
    return jsonify({"error": "Authentication required"}), 401


def register_error_handlers(app):
    """Central error handling: JSON responses for common HTTP errors.
       Flask's default errors are HTML; for an API we override with JSON."""

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(500)
    def server_error(e):
        # log the real error here in production (sentry), return a safe message
        app.logger.error("500: %s", e)
        return jsonify({"error": "Internal server error"}), 500
