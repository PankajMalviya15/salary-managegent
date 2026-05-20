"""
Database engine, session factory, and declarative Base.

Uses SQLite by default (from DATABASE_URL env var).
The `check_same_thread` connect arg is required for SQLite
when the engine is shared across threads (e.g. FastAPI workers).

Connection pooling is configured for production use:
- pool_size=5: maintains 5 persistent connections in the pool.
  Suitable for a single-HR-user tool with 10k employees — most
  requests are short-lived reads that return quickly.
- max_overflow=10: allows up to 10 additional temporary connections
  during traffic bursts (e.g. bulk analytics queries while an admin
  is also editing employees). These overflow connections are discarded
  once idle.
- pool_pre_ping=True: validates connections before use, preventing
  "stale connection" errors after database restarts.

Note: SQLite ignores pool_size/max_overflow (uses StaticPool
internally), but these settings apply when switching to Postgres.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./salary_management.db")

# ── Engine ──────────────────────────────────────────────────────────

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
    # Connection pooling config (applies to Postgres/MySQL, ignored by SQLite)
    pool_size=5,
    max_overflow=10,
)

# ── Session factory ─────────────────────────────────────────────────

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Declarative Base ────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""
    pass


# ── Dependency for FastAPI ──────────────────────────────────────────

def get_db():
    """
    FastAPI dependency that yields a database session
    and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
