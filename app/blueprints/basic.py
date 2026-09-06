# =============================================================================
# app/blueprints/basic.py  --  LEVEL 1 (BASIC) : Flask routing fundamentals
# =============================================================================
# No DB, no auth — just the request/response surface of Flask so you learn the
# core routing and request API before the rest.
#
# CONCEPTS (basic):
#   * @bp.route("/path", methods=[...]) — the core decorator
#   * variable rules: /item/<int:item_id>  (typed converters)
#   * request.args  : query string (?a=1)
#   * request.json  : parsed JSON body
#   * jsonify(...)  : turn a dict/list into a JSON response
#   * status codes as second return value: return jsonify(...), 201

from flask import Blueprint, jsonify, request

# Blueprint: name + url_prefix. This module handles /api/basic/...
bp = Blueprint("basic", __name__, url_prefix="/api/basic")

# in-memory store (dict) so we can demo CRUD without SQL yet
ITEMS: dict[int, dict] = {}


# --- 1) simplest route --------------------------------------------------------
@bp.route("/hello", methods=["GET"])
def hello():
    # jsonify serializes dict/list -> JSON response with content-type application/json
    return jsonify({"message": "Hello, world!"})


# --- 2) path parameters + type converter --------------------------------------
# <int:item_id> converter ensures item_id is an int, else Flask 404s.
@bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id: int):
    item = ITEMS.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


# --- 3) query parameters -------------------------------------------------------
@bp.route("/items", methods=["GET"])
def list_items():
    # request.args is an ImmutableMultiDict of the query string
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    page = list(ITEMS.values())[skip : skip + limit]
    return jsonify({"total": len(ITEMS), "items": page})


# --- 4) request body + create ---------------------------------------------------
@bp.route("/items", methods=["POST"])
def create_item():
    # request.json returns the parsed JSON body (or None if not JSON).
    data = request.json or {}
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 422
    new_id = max(ITEMS, default=0) + 1
    ITEMS[new_id] = {"id": new_id, "name": data["name"], "price": data.get("price", 0)}
    return jsonify(ITEMS[new_id]), 201


# --- 5) update (full replace) ----------------------------------------------------
@bp.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id: int):
    if item_id not in ITEMS:
        return jsonify({"error": "Item not found"}), 404
    data = request.json or {}
    ITEMS[item_id].update({"name": data.get("name", ITEMS[item_id]["name"]),
                           "price": data.get("price", ITEMS[item_id]["price"])})
    return jsonify(ITEMS[item_id])


# --- 6) delete -------------------------------------------------------------------
@bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id: int):
    if item_id not in ITEMS:
        return jsonify({"error": "Item not found"}), 404
    ITEMS.pop(item_id)
    return jsonify({"ok": True}), 204   # 204 + no body (jsonify ignored on 204)
