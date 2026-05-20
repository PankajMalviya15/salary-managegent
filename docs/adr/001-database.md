# ADR-001: Database Choice — SQLite for Development, Postgres-Ready via SQLAlchemy

**Status:** Accepted  
**Date:** 2024-01-15  
**Decision:** Use SQLite as the default development database with SQLAlchemy as the ORM abstraction layer.

## Context

The Salary Management Tool needs a relational database to store 10,000+ employee records with complex analytics queries. The team needs a zero-config local setup that any engineer can start in under 60 seconds.

## Decision

We chose **SQLite for development** with **SQLAlchemy ORM** so the database engine is swappable.

## Rationale

- **Zero-config**: SQLite requires no database server installation, no port binding, no credentials. `make setup && make seed` is all a new engineer needs.
- **File-portable**: The `.db` file can be copied, shared, or deleted trivially.
- **SQLAlchemy abstraction**: All queries use SQLAlchemy's expression language and ORM, not raw SQL. Switching to Postgres requires only changing `DATABASE_URL`.
- **Sufficient for scope**: A single-HR-user tool with 10k records is well within SQLite's capabilities.

## Trade-offs

- SQLite lacks some Postgres features (`WIDTH_BUCKET`, `LATERAL JOIN`, advisory locks).
- Connection pooling settings (`pool_size`, `max_overflow`) are ignored by SQLite but configured for when the switch happens.
- `check_same_thread=False` is required for FastAPI's threaded workers.

## Migration Path

1. `pip install psycopg2-binary`
2. `DATABASE_URL=postgresql://user:pass@localhost:5432/salary_management`
3. `make migrate && make seed`
