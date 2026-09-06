# =============================================================================
# python_scripts/01_basics.py  --  LEVEL: BASIC  (Flask-flavoured)
# =============================================================================
# Purpose: Python fundamentals you'll use writing EVERY Flask file (routing,
# models, blueprints). Flask is synchronous, so the basics here are the core
# building blocks — run top to bottom.
# Run:  .venv/bin/python python_scripts/01_basics.py
#
# Topics: variables & types, strings, lists/dicts, comprehensions, functions,
#         args/kwargs, exceptions — the essentials.

def main() -> None:
    # --- variables & type hints ------------------------------------------
    title: str = "My Flask Post"
    views: int = 120
    rating: float = 4.7
    published: bool = True
    tags: list[str] = ["flask", "python"]
    meta: dict[str, str] = {"author": "alice"}

    # --- strings (f-strings are the modern choice) ------------------------
    slug = title.lower().replace(" ", "-")
    print(f"slug: {slug}")

    # --- lists -------------------------------------------------------------
    posts = ["post-1", "post-2", "post-3"]
    posts.append("post-4")                      # add to end
    first, *rest = posts                        # destructuring
    print("first:", first, "rest:", rest)

    # --- dicts (the backbone of JSON responses) ---------------------------
    record = {"id": 1, "title": title}
    record["views"] = views                     # add a key
    print("record views:", record.get("views", 0))
    print("missing key default:", record.get("nope", "default"))

    # --- list comprehension (very common in Flask code) --------------------
    ids = [p["id"] for p in [{"id": i} for i in range(3)]]
    print("ids:", ids)

    # --- functions + keyword-only args -------------------------------------
    def render(name: str, *, template: str = "base") -> str:
        """Return a fake rendered string. `*` forces template to be named."""
        return f"{template} for {name}"

    print(render("Home", template="page"))

    # --- *args / **kwargs ---------------------------------------------------
    def log(*args, **kwargs) -> None:
        print("args:", args, "kwargs:", kwargs)

    log("hello", level="info")

    # --- exceptions: catch specific types, use finally for cleanup ----------
    try:
        risky = int("not-a-number")
    except ValueError as exc:
        print("caught ValueError:", exc)
    finally:
        print("cleanup runs always")


if __name__ == "__main__":
    # This guard lets us import this file without running it
    main()
