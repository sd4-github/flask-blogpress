# =============================================================================
# app/blueprints/auth.py  --  LEVEL 2-3 : session-based authentication
# =============================================================================
# CONTRAST WITH FASTAPI (interview question!):
#   * FastAPI/JWT : the server mints a signed token; NO server-side session.
#   * Flask-Login : the server stores a SESSION (server-side) keyed by a cookie.
#     login_user() -> sets session cookie; current_user -> the logged-in User.
#     @login_required -> gate a route behind auth.
#
# REGISTER/LOGIN here return JSON (we're pure backend).

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import User
from app.schemas import user_create_schema, user_schema

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# --- register ---------------------------------------------------------------
@bp.route("/register", methods=["POST"])
def register():
    """Create an account. Emails must be unique (409 on conflict)."""
    data = request.json or {}
    errors = user_create_schema.validate(data)
    if errors:
        # Marshmallow validation failed -> 422 with the field errors
        return jsonify({"errors": errors}), 422

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(email=data["email"])
    user.set_password(data["password"])      # hashes internally (no raw store)
    db.session.add(user)
    db.session.commit()
    # dump the public representation (role unchanged, no password)
    return jsonify(user_schema.dump(user)), 201


# --- login ------------------------------------------------------------------
@bp.route("/login", methods=["POST"])
def login():
    """Exchange email+password for a session cookie."""
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    # Use a generic error so we don't reveal whether an email exists.
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)                     # -> Flask sets the session cookie
    return jsonify({"message": "Logged in", "user": user_schema.dump(user)})


# --- logout -----------------------------------------------------------------
@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Destroy the server-side session."""
    logout_user()                        # remove the session cookie
    return jsonify({"message": "Logged out"})


# --- who am i ---------------------------------------------------------------
@bp.route("/me", methods=["GET"])
@login_required
def me():
    """Return the currently logged-in user (requires a valid session)."""
    # current_user is injected by Flask-Login from the session cookie.
    return jsonify(user_schema.dump(current_user))
