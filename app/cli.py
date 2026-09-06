# =============================================================================
# app/cli.py  --  custom `flask` CLI commands
# =============================================================================
# Flask lets you add your own commands runnable as `flask <command>`,
# e.g. `flask seed-demo`. Great for adding ops/admin workflows and a common
# interview question. The click package (bundled with Flask) defines them.
#
#   FLASK_APP=run.py flask seed-demo

import click
from flask import current_app

from app.extensions import db
from app.models import Post, User


@click.command("seed-demo")
def seed_demo_command():
    """Create sample users + posts (idempotent: won't duplicate emails)."""
    # current_app is the request-context proxy to the active Flask app.
    demo_emails = ["alice@example.com", "bob@example.com"]
    for email in demo_emails:
        if User.query.filter_by(email=email).first():
            click.echo(f"skip {email} (exists)")
            continue
        u = User(email=email, role="author")
        u.set_password("secret123")
        db.session.add(u)
        db.session.commit()
        # each user gets one demo post
        db.session.add(Post(title=f"Hello from {email.split('@')[0]}", body="demo body", author=u))
        db.session.commit()
        click.echo(f"seeded {email}")

    click.echo("Done. Try `flask run` then hit /api/posts")


def register_commands(app) -> None:
    """Attach all custom commands to a given app."""
    app.cli.add_command(seed_demo_command)
