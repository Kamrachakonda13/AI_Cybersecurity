"""VEYRA database session layer (SQLAlchemy 2.0).

Help — what this file does and what depends on it:
- `DATABASE_URL`: read from env; Docker Compose supplies
  `postgresql+psycopg://veyra:veyra@postgres:5432/veyra`, otherwise falls back
  to local `sqlite:///./veyra.db` (with `check_same_thread=False`).
- `engine` / `SessionLocal`: shared connection pool + session factory used by
  every route via the `get_db` dependency and by `app.main.lifespan` for seeding.
- `Base` (DeclarativeBase): every model in `app.models.entities` subclasses it,
  which is how `Base.metadata.create_all()` in `app.main` creates all tables.
- `get_db`: FastAPI dependency yielding one session per request (always closed).
  Depends on: `DATABASE_URL` env, SQLAlchemy. Depended on by: every endpoint in
  `app.api.routes` and every service taking a `db: Session` (`graph`, `visibility`).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./veyra.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
