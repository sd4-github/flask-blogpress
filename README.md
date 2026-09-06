# BlogPress

A **Flask** blog platform REST API built for backend interview preparation (~5 YOE depth). Covers Flask fundamentals through advanced features like session-based auth, Celery background tasks, Redis caching, and server-sent events.

[GitHub](https://github.com/sd4-github/flask-blogpress)

## What It Does

- **Register & login** with session-based auth (Flask-Login)
- **CRUD blog posts** with role-based access (reader/author/admin) and ownership enforcement
- **Advanced features**: file uploads, Celery background tasks, Redis caching, server-sent events

## Tech Stack

| Layer | Tech |
|-------|------|
| Framework | [Flask](https://flask.palletsprojects.com/) 3.0 |
| WSGI Server | Gunicorn |
| ORM | SQLAlchemy (Flask-SQLAlchemy) |
| Database | PostgreSQL |
| Auth | Session-based (Flask-Login) |
| Serialization | Marshmallow |
| Background Tasks | Celery + Redis |
| Caching | Redis |
| Testing | pytest |

## Project Structure

```
app/
├── __init__.py          # App factory (create_app)
├── config.py            # Config classes (Dev/Prod/Test)
├── extensions.py        # Flask extensions (db, login_manager, migrate)
├── models.py            # SQLAlchemy models (User, Post)
├── schemas.py           # Marshmallow serialization/validation
├── tasks.py             # Celery app and tasks
├── cli.py               # Custom CLI command (seed-demo)
└── blueprints/
    ├── basic.py         # Level 1: routing, in-memory CRUD
    ├── auth.py          # Level 2-3: session-based auth
    ├── posts.py         # Level 2-3: DB CRUD, roles, ownership
    └── advanced.py      # Level 3: uploads, Celery, Redis, SSE
tests/                   # pytest test suite
```

## Quick Start

```bash
# Prerequisites: PostgreSQL + Redis running locally

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the dev server
FLASK_APP=run.py flask run

# Seed demo users and posts
FLASK_APP=run.py flask seed-demo
```

API available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/basic/hello` | No | Hello world |
| `GET/POST` | `/api/basic/items` | No | In-memory CRUD |
| `POST` | `/api/auth/register` | No | Register user |
| `POST` | `/api/auth/login` | No | Login (session cookie) |
| `POST` | `/api/auth/logout` | Yes | Logout |
| `GET` | `/api/auth/me` | Yes | Current user profile |
| `GET/POST` | `/api/posts` | No/Yes* | List/create posts |
| `GET/PATCH/DELETE` | `/api/posts/{id}` | No/Yes* | Single post CRUD |
| `POST` | `/api/advanced/upload` | Yes | File upload |
| `POST` | `/api/advanced/digest` | Yes | Background task |
| `GET` | `/api/advanced/cached-time` | Yes | Redis cache demo |
| `GET` | `/api/advanced/events` | No | Server-sent events |

*Create requires author/admin role

## Interview Topics Covered

- App factory pattern, blueprints, extension factories
- Session-based vs JWT auth trade-offs
- Marshmallow serialization, request validation
- Role-based access control, row-level ownership
- Celery background tasks with Redis broker
- Redis caching with TTL
- Server-sent events
- File uploads, custom CLI commands
- Testing with Flask test client

See [INTERVIEW_TOPICS.md](INTERVIEW_TOPICS.md) for the full topic-to-file mapping.
