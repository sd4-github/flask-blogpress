# BlogPress — Flask: Interview Topics Covered

> Pure-backend Flask blog API. **Basic → Intermediate → Advanced**, ~5 YOE depth.
> Each row maps a likely **interview question/topic** to the **file(s)** where it's answered in code.

---

## 1. Python fundamentals
| Topic / question | Where covered |
|------------------|---------------|
| Types, f-strings, control flow, functions | [python_scripts/01_basics.py](python_scripts/01_basics.py) |
| OOP (classes, inheritance, magic methods) + context managers | [python_scripts/02_oop_and_context.py](python_scripts/02_oop_and_context.py) |
| Threading, GIL, concurrency | [python_scripts/03_threading_advanced.py](python_scripts/03_threading_advanced.py) |

## 2. Flask framework core
| Topic / question | Where covered |
|------------------|---------------|
| App factory pattern (`create_app`) | [app/__init__.py](app/__init__.py) |
| Blueprints (modular routing) | [app/blueprints/](app/blueprints/) |
| Basic REST: GET/POST/PUT/DELETE + path params | [app/blueprints/basic.py](app/blueprints/basic.py) |
| Request parsing & JSON body | [app/blueprints/basic.py](app/blueprints/basic.py) |
| Config classes & env loading | [app/config.py](app/config.py) |
| Extension factories (db, migrate, login, mail) | [app/extensions.py](app/extensions.py) |
| Models (User/Post), relationships | [app/models.py](app/models.py) |
| Schema serialization (Marshmallow) | [app/schemas.py](app/schemas.py) |
| CLI commands | [app/cli.py](app/cli.py) |
| App entrypoint + run | [run.py](run.py) |

## 3. Auth (Flask-Login sessions)
| Topic / question | Where covered |
|------------------|---------------|
| Register / login / logout | [app/blueprints/auth.py](app/blueprints/auth.py) |
| Session-based auth (`login_user`, `@login_required`) | [app/blueprints/auth.py](app/blueprints/auth.py) |
| Current-user access in views | [app/blueprints/posts.py](app/blueprints/posts.py) |
| Authorization (owner-only edit) `_can_edit` | [app/blueprints/posts.py](app/blueprints/posts.py) |

## 4. Advanced Flask topics
| Topic / question | Where covered |
|------------------|---------------|
| File upload (multipart, streamed to disk) | [app/blueprints/advanced.py](app/blueprints/advanced.py) |
| Redis caching with per-user TTL keys | [app/blueprints/advanced.py](app/blueprints/advanced.py) |
| Server-Sent Events (SSE streaming) | [app/blueprints/advanced.py](app/blueprints/advanced.py) |
| Celery background tasks | [app/tasks.py](app/tasks.py) |

## 5. Testing
| Topic / question | Where covered |
|------------------|---------------|
| Test client + fixtures | [tests/conftest.py](tests/conftest.py) |
| Auth + basic endpoint tests | [tests/test_basic_auth.py](tests/test_basic_auth.py) |
| Posts CRUD tests | [tests/test_posts.py](tests/test_posts.py) |
| Full-stack smoke test of every feature | [smoke_test.py](smoke_test.py) |

---

### How to explore
Start with `python_scripts/01_basics.py`, then `app/__init__.py` (app factory) → `app/config.py` → `app/models.py` → `app/blueprints/*` in order. Every file is heavily commented with **why**, not just *what*.
