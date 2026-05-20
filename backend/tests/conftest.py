"""
Shared test configuration — provides a test database
and overrides FastAPI's get_db dependency for all API tests.
"""

from datetime import date

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.job_title import JobTitle
from app.models.department import Department
from app.models.employee import Employee


# ── Shared test engine (file-based so same DB is visible across connections) ──

TEST_DB_URL = "sqlite:///./test_salary_management.db"

TEST_ENGINE = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)

# Enable FK enforcement for SQLite
@event.listens_for(TEST_ENGINE, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestSession = sessionmaker(bind=TEST_ENGINE)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


# Override at module level so it applies to ALL tests
app.dependency_overrides[get_db] = override_get_db


# ── Fixtures ───────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture
def db_session():
    """Provide a test database session."""
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seed_lookups(db_session):
    """Seed job titles and departments for tests that need them."""
    db_session.add_all([
        JobTitle(id=1, title="Software Engineer"),
        JobTitle(id=2, title="Data Scientist"),
        Department(id=1, name="Engineering"),
        Department(id=2, name="Data Science"),
    ])
    db_session.commit()


@pytest.fixture
def seed_analytics_data(seed_lookups, db_session):
    """Seed 5 employees across 2 countries for analytics tests."""
    employees = [
        Employee(
            full_name="Alice", email="alice@test.com",
            job_title_id=1, department_id=1, country="US",
            salary=100000, currency="USD", employment_type="full-time",
            hire_date=date(2023, 1, 1), is_active=True,
        ),
        Employee(
            full_name="Bob", email="bob@test.com",
            job_title_id=1, department_id=1, country="US",
            salary=120000, currency="USD", employment_type="full-time",
            hire_date=date(2023, 6, 1), is_active=True,
        ),
        Employee(
            full_name="Carol", email="carol@test.com",
            job_title_id=1, department_id=1, country="US",
            salary=80000, currency="USD", employment_type="full-time",
            hire_date=date(2024, 1, 1), is_active=True,
        ),
        Employee(
            full_name="Dave", email="dave@test.com",
            job_title_id=2, department_id=2, country="GB",
            salary=90000, currency="GBP", employment_type="full-time",
            hire_date=date(2023, 3, 1), is_active=True,
        ),
        Employee(
            full_name="Eve", email="eve@test.com",
            job_title_id=2, department_id=2, country="GB",
            salary=95000, currency="GBP", employment_type="contract",
            hire_date=date(2024, 2, 1), is_active=True,
        ),
    ]
    db_session.add_all(employees)
    db_session.commit()


@pytest_asyncio.fixture
async def client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
