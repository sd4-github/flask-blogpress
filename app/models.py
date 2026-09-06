# =============================================================================
# app/models.py  --  SQLAlchemy models (User, Post)
# =============================================================================
# Flask-SQLAlchemy models inherit from `db.Model`. Same ORM ideas as FastAPI
# but with a Flask-flavored API (db.Column, db.relationship).
#
# AUTH: uses werkzeug.security to hash/verify passwords (no plaintext).
# Flask-Login needs `is_authenticated`, `is_active`, etc. — UserMixin provides
# them. We only override what we need.

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """A registered author. UserMixin gives Flask-Login the required methods."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    # 0 = reader, 1 = author, 2 = admin  (a simple role enum we can check)
    role = db.Column(db.String(20), default="reader")
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # relationship: user.posts -> their posts; delete user deletes posts (cascade)
    posts = db.relationship("Post", back_populates="author", cascade="all, delete-orphan")

    # --- password handling (never store raw) ---------------------------------
    def set_password(self, password: str) -> None:
        # werkzeug generates a salted, one-way hash.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # --- convenience for new writers -----------------------------------------
    @property
    def is_author(self) -> bool:
        return self.role in ("author", "admin")

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Post(db.Model):
    """A blog post created by a User."""
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # foreign key: each post belongs to exactly one user
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post {self.title!r}>"
