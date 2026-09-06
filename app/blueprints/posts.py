# =============================================================================
# app/blueprints/posts.py  --  LEVEL 2-3 : REST API with DB + auth + roles
# =============================================================================
# Demonstrates a proper JSON REST API:
#   * create/list/read/update/delete posts (owned by users)
#   * Marshmallow validates bodies; we return 422 on bad input
#   * @login_required + role checks (write access only for authors/admins)
#   * row-level access: to edit a post you must be its author OR an admin
#   * pagination via ?page=&per_page=

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Post
from app.schemas import post_schema, post_update_schema, posts_schema

bp = Blueprint("posts", __name__, url_prefix="/api/posts")


# --- list (public, paginated) --------------------------------------------------
@bp.route("", methods=["GET"])
def list_posts():
    """Public: list published posts, paginated.
       Flask-SQLAlchemy paginate() returns a Pagination with .items/.total/.pages."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)  # cap it!
    # only show published posts to anonymous readers
    query = Post.query.filter(Post.published.is_(True)).order_by(Post.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": posts_schema.dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
    })


# --- create (author/admin only) --------------------------------------------------
@bp.route("", methods=["POST"])
@login_required
def create_post():
    """Only users with an author/admin role may write posts."""
    if not current_user.is_author:
        return jsonify({"error": "Forbidden: author role required"}), 403

    data = request.json or {}
    errors = post_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 422

    post = Post(title=data["title"], body=data["body"],
                published=data.get("published", False), author=current_user)
    db.session.add(post)
    db.session.commit()
    return jsonify(post_schema.dump(post)), 201


# --- read one ----------------------------------------------------------------
@bp.route("/<int:post_id>", methods=["GET"])
def get_post(post_id: int):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    # draft posts hidden from the public (unless it's the author)
    if not post.published and (not current_user.is_authenticated or post.author_id != current_user.id):
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post_schema.dump(post))


# --- update (partial) ------------------------------------------------------------
@bp.route("/<int:post_id>", methods=["PATCH"])
@login_required
def update_post(post_id: int):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if not _can_edit(current_user, post):
        return jsonify({"error": "Forbidden: not your post"}), 403

    data = request.json or {}
    # exclude_unset-like: only apply keys that were sent
    for field in ("title", "body", "published"):
        if field in data:
            setattr(post, field, data[field])
    db.session.commit()
    return jsonify(post_schema.dump(post))


# --- delete ---------------------------------------------------------------------
@bp.route("/<int:post_id>", methods=["DELETE"])
@login_required
def delete_post(post_id: int):
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if not _can_edit(current_user, post):
        return jsonify({"error": "Forbidden: not your post"}), 403
    db.session.delete(post)
    db.session.commit()
    return jsonify({"ok": True}), 204


# --- private helper --------------------------------------------------------------
def _can_edit(user, post) -> bool:
    """An author can edit their own post; an admin can edit anything."""
    return post.author_id == user.id or user.role == "admin"
