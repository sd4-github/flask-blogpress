# BlogPress API — Architecture & Implementation Guide

A **pure-backend** Flask REST API built to teach every essential Flask feature from
**basic → intermediate → advanced**, for a 5-YOE backend interview.

Read top-to-bottom. Each section explains **what**, **why**, and **where in code**.

---

## 1. Project layout

```
2_flask_blogpress/
├── run.py                     # entry point (create_app(DevelopmentConfig))
├── app/
│   ├── __init__.py            # app FACTORY: config, extensions, blueprints, errors
│   ├── config.py              # per-environment config classes (dev/prod/test)
│   ├── extensions.py          # db / login_manager / migrate instances
│   ├── models.py              # SQLAlchemy models: User, Post
│   ├── schemas.py             # Marshmallow schemas (JSON validation)
│   ├── cli.py                 # custom `flask` commands (seed-demo)
│   ├── tasks.py               # Celery workers (durable background jobs)
│   └── blueprints/
│       ├── basic.py           # LEVEL 1  — routing, params, body, in-memory CRUD
│       ├── auth.py            # LEVEL 2-3— session login/logout
│       ├── posts.py           # LEVEL 2-3— REST CRUD + roles + ownership
│       └── advanced.py        # LEVEL 3  — uploads, Celery, Redis cache, SSE
├── tests/                     # pytest (11 tests pass)
├── python_scripts/            # 01 basics, 02 OOP+context, 03 threading
├── smoke_test.py              # verifies advanced features end-to-end
└── .env / .gitignore / requirements.txt
```

### The Flask app factory pattern (industry standard)
Unlike FastAPI's single `app` object, Flask builds the app from a **factory**:
```python
def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)   # dev/prod/test settings
    db.init_app(app); migrate.init_app(app); login_manager.init_app(app)
    app.register_blueprint(basic.bp)       # ... each modular router
    register_error_handlers(app)
    return app
```
Benefits: fresh app per test, multiple configs, no circular imports — a common
interview question ("why an app factory in Flask?").

---

## 2. Blueprints vs FastAPI routers (contrast)
- FastAPI: `APIRouter` + tags + auto-OpenAPI docs.
- Flask: **Blueprints** — each `Blueprint("name", url_prefix="/api/...")` groups
  related routes. Registered in the factory.
Same goal (modular routing), different mechanics.

---

## 3. Feature walkthrough (basic → advanced)

### LEVEL 1 — Basics (`blueprints/basic.py`)
| Feature | Where | What it teaches |
|---|---|---|
| Routing | `@bp.route("/", methods=[...])` | Maps URL + HTTP method to a function |
| Path params | `/items/<int:item_id>` | Typed URL converters |
| Query params | `request.args.get("skip", type=int)` | Read + cast query string |
| Request body | `request.json` | Parsed JSON body |
| Response | `jsonify(...)` | Turn dict/list into JSON |
| Status codes | `return jsonify(...), 201` | Explicit HTTP status |

### LEVEL 2 — Intermediate (`blueprints/posts.py`, `models.py`, `schemas.py`)
| Feature | Where | What it teaches |
|---|---|---|
| Flask-SQLAlchemy | `models.py` | `db.Model` ORM to Postgres |
| Marshmallow | `schemas.py` | Separate JSON validate/serialize (vs Pydantic) |
| Session auth | `blueprints/auth.py` | Flask-Login: `login_user`, `current_user` |
| Role checks | `posts.py` | `@login_required` + `is_author` permissions |
| Pagination | `posts.py` | `query.paginate(page, per_page)` |
| Row-level ownership | `_can_edit` | Author edits own, admin edits all |

### LEVEL 3 — Advanced (`blueprints/advanced.py`, `tasks.py`)
| Feature | Where | What it teaches |
|---|---|---|
| File uploads | `advanced.py` | `request.files`, stream to disk, extension checks |
| Celery tasks | `tasks.py` | Durable/retryable background queue via Redis |
| Redis cache | `advanced.py` | Cache slow responses (TTL), per-user key |
| SSE streaming | `advanced.py` | Server-Sent Events for live push |
| CLI commands | `cli.py` | `flask seed-demo` custom commands |
| Error handlers | `__init__.py` | JSON 404/400/500 instead of HTML |

### FastAPI vs Flask on the SAME problems (interview gold)
| Problem | FastAPI | Flask |
|---|---|---|
| Validation | Pydantic (built-in) | Marshmallow (add-on) |
| Auth | JWT (stateless) | Server-side session (Flask-Login) |
| Concurrency | async event loop | threads / WSGI workers |
| Background | BackgroundTasks / Celery | Celery |
| Docs | auto /docs | none built-in |

---

## 4. Security model (session-based, contrast with FastAPI's JWT)
1. **Register** → hash password with `werkzeug.security` (never plaintext).
2. **Login** → `login_user(user)` sets an encrypted **session cookie**;
   the server holds the session state.
3. **Protected route** → `@login_required` + Flask-Login resolves `current_user`
   from the cookie via `user_loader`.
4. **Role control** → `current_user.is_author` gates writes; admins bypass ownership.

Choosing between JWT vs sessions is a top interview question: JWT = stateless/scalable
but harder to revoke; sessions = revocable/server-controlled but need shared storage.

---

## 5. How to run it
```bash
cd 2_flask_blogpress
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
FLASK_APP=run.py .venv/bin/flask run          # dev server on :5000
FLASK_APP=run.py .venv/bin/flask seed-demo    # add sample users/posts
# run a Celery worker (optional)
.venv/bin/celery -A app.tasks.celery_app worker --loglevel=info
```

### Tests
```bash
.venv/bin/python -m pytest -q                 # 11 tests
.venv/bin/python smoke_test.py               # advanced features
```

---

## 6. Interview Q&A this prepares you for
- App factory vs single instance — why?
- JWT vs server-side sessions — trade-offs, when to use which.
- Blueprints & core vs extension philosophy ("micro-framework").
- How do you make a Flask API return JSON errors / protect against CSRF?
- How do you run background jobs and cache responses in Flask?
- Thread-safety with a shared SQLAlchemy session across requests.
