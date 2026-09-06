# =============================================================================
# python_scripts/02_oop_and_context.py  --  LEVEL: INTERMEDIATE (Flask-flavoured)
# =============================================================================
# Purpose: the language features behind Flask's models, schemas, and blueprints.
#   * OOP: classes, inheritance, @property, magic methods  (like our models)
#   * @property decorator  (e.g. User.is_author in models.py)
#   * context managers     (e.g. the app/app-request context)
#   * dataclasses
# Run:  .venv/bin/python python_scripts/02_oop_and_context.py

# --- 1) Classes & magic methods -------------------------------------------------
# Every Flask model is a class. Magic methods (__repr__, __eq__) customize
# behaviour; the interpreter calls them automatically.
class Post:
    def __init__(self, title: str, body: str, *, published: bool = False):
        self.title = title
        self.body = body
        self.published = published

    # __repr__ : what repr(obj) prints (debugging, logs, Flask shell)
    def __repr__(self) -> str:
        return f"<Post {self.title!r}>"

    # `len(post)` uses __len__
    def __len__(self) -> int:
        return len(self.body)

    # equality: `post1 == post2`
    def __eq__(self, other) -> bool:
        if not isinstance(other, Post):
            return NotImplemented
        return self.title == other.title and self.body == other.body

p1 = Post("Hello", "some body")
p2 = Post("Hello", "some body")
print(p1)                       # uses __repr__
print("len:", len(p1))          # uses __len__
print("equal:", p1 == p2)       # uses __eq__


# --- 2) Inheritance -----------------------------------------------------------------
# A base class holds shared behaviour; subclasses specialise it.
class BaseModel:
    id_counter = 0                      # class attribute (shared)

    def __init__(self):
        type(self).id_counter += 1
        self.id = type(self).id_counter

    def save(self) -> None:
        print(f"saved {self} (mock)")

class Article(BaseModel):
    def __init__(self, slug: str):
        super().__init__()              # call the parent's __init__
        self.slug = slug

    def __repr__(self) -> str:
        return f"<Article {self.slug}>"

a = Article("first-article")
print(a, "id =", a.id)
a.save()


# --- 3) @property ---------------------------------------------------------------------
# A property is a method accessed like an attribute. It lets you compute values
# and add read-only/validation logic WITHOUT changing the public API.
# Compare: User.is_author in app/models.py
class User:
    def __init__(self, email: str, role: str = "reader"):
        self._email = email
        self.role = role

    @property
    def is_author(self) -> bool:
        return self.role in ("author", "admin")

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        # validation lives in the setter — clean & reusable
        if "@" not in value:
            raise ValueError("invalid email")
        self._email = value

u = User("a@b.com", "author")
print("is_author:", u.is_author)       # accessed like a field, not a call
u.email = "new@domain.com"              # calls the setter
print("email changed:", u.email)


# --- 4) Context managers (with ...) ----------------------------------------------------
# The `with` statement guarantees enter/exit even on exceptions. Flask's app/request
# contexts work this way:
#     with app.app_context():
#         ...  # db.session available here, cleaned up after
class DBConnection:
    def __enter__(self):
        print("[enter] opening connection")
        return self                     # becomes the `as x` value

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[exit] closing connection (exc_type={exc_type})")
        return False                    # False => propagate exceptions

with DBConnection() as conn:
    print("do work")

# contextlib.contextmanager turns a generator into a context manager (less boilerplate)
from contextlib import contextmanager

@contextmanager
def transaction():
    print("BEGIN")
    try:
        yield                          # the body of `with` runs here
    finally:
        print("COMMIT/ROLLBACK")

with transaction():
    print("inside transaction")


# --- 5) dataclasses -------------------------------------------------------------------
from dataclasses import dataclass, field

@dataclass
class Config:
    secret_key: str
    debug: bool = False
    whitelist: list[str] = field(default_factory=list)   # mutable default MUST use factory

cfg = Config("k")
cfg.whitelist.append("127.0.0.1")
print("cfg:", cfg)
