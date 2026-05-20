"""
Database engine, session factory, and declarative Base.

Uses SQLite by default (from DATABASE_URL env var).
The `check_same_thread` connect arg is required for SQLite
when the engine is shared across threads (e.g. FastAPI workers).
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
