# =============================================================================
# app/schemas.py  --  Marshmallow schemas (serialize / validate JSON)
# =============================================================================
# COMPARE WITH FASTAPI (interview gold):
#   * FastAPI  uses Pydantic  -> validation baked into the framework.
#   * Flask    uses Marshmallow-> a SEPARATE library you wire up yourself.
#     Marshmallow SCHEMAS:
#       - dump()      : object  -> JSON-ready dict
#       - load()      : dict    -> validated object (raises ValidationError)
#       - fields.*    : declare type/constraints
#   This is the Flask-idiomatic way to build a clean JSON REST API.

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class UserSchema(Schema):
    """How a user appears in the API (single or many)."""
    id = fields.Int(dump_only=True)          # dump_only: never accept from client
    email = fields.Email(required=True)
    role = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class UserCreateSchema(Schema):
    """Input for creating a user. Password is write-only (never dumped)."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    # NOT exposing role: it would let anyone self-promote. Admin sets it.


class PostSchema(Schema):
    """How a post appears in the API."""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    body = fields.Str(required=True)
    published = fields.Bool(load_default=False)
    created_at = fields.DateTime(dump_only=True)
    # nested author -> includes the author's public info in the JSON
    author = fields.Nested(UserSchema, dump_only=True)


class PostUpdateSchema(Schema):
    """Optional fields for partial updates."""
    title = fields.Str(validate=validate.Length(min=1, max=200))
    body = fields.Str()
    published = fields.Bool()


# Instances we can reuse across blueprints.
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_create_schema = UserCreateSchema()
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
post_update_schema = PostUpdateSchema()
