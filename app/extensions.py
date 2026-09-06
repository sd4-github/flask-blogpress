# =============================================================================
# app/extensions.py  --  instantiate Flask extensions ONCE, attach later
# =============================================================================
# WHY THIS FILE? (important Flask pattern / interview question)
#   In the app-factory pattern we create extensions WITHOUT an app, then bind
#   them to the app inside create_app() with init_app(). This avoids circular
#   imports (models import db; app imports models; db must exist first).
#
# Flat structure: one file for all global extensions = simple & readable here.
# Larger projects split them, but this is the canonical small-app layout.

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance, usable as `db.Model`, `db.session`, `db.Column` later.
db = SQLAlchemy()

# Handles server-side session auth: login_user(), current_user, login_required.
login_manager = LoginManager()

# Wraps Alembic migrations into `flask db ...` commands.
migrate = Migrate()
