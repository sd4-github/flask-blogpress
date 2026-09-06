# =============================================================================
# run.py  --  Flask entry point
# =============================================================================
# Usage:
#   FLASK_APP=run.py flask run          # dev server
#   FLASK_APP=run.py flask seed-demo    # add demo users/posts
#   FLASK_APP=run.py .venv/bin/python run.py   # same as run

from app import create_app
from app.config import DevelopmentConfig

# Create the app with dev settings. FLASK_APP=run.py + `flask run` uses this too.
app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
