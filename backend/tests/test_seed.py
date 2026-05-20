"""
Test seed script — verifies seeding produces correct, consistent data.

Runs the seed with --count 100 against an in-memory SQLite database
and asserts row counts, email uniqueness, and country validity.
"""

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.job_title import JobTitle
from app.models.department import Department
from app.models.employee import Employee
from seed.seed import seed, COUNTRIES, JOB_TITLES, DEPARTMENTS


@pytest.fixture
def seeded_session():
    """Create an in-memory DB, run seed with 100 rows, yield session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    # Run seed
    seed(count=100, engine=engine)

    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


class TestSeedRowCounts:
    def test_employee_count(self, seeded_session):
        """Seed with --count 100 should produce exactly 100 employee rows."""
        count = seeded_session.scalar(select(func.count()).select_from(Employee))
        assert count == 100

    def test_job_title_count(self, seeded_session):
        """Should have exactly 15 job titles."""
        count = seeded_session.scalar(select(func.count()).select_from(JobTitle))
        assert count == len(JOB_TITLES)

    def test_department_count(self, seeded_session):
        """Should have exactly 10 departments."""
        count = seeded_session.scalar(select(func.count()).select_from(Department))
        assert count == len(DEPARTMENTS)


class TestSeedDataIntegrity:
    def test_no_duplicate_emails(self, seeded_session):
        """All employee emails must be unique."""
        emails = [
            row[0]
            for row in seeded_session.execute(select(Employee.email)).all()
        ]
        assert len(emails) == len(set(emails)), "Duplicate emails found!"

    def test_countries_in_allowed_set(self, seeded_session):
        """Every employee country must be in the COUNTRIES list."""
        countries = {
            row[0]
            for row in seeded_session.execute(
                select(Employee.country).distinct()
            ).all()
        }
        assert countries.issubset(set(COUNTRIES)), (
            f"Invalid countries found: {countries - set(COUNTRIES)}"
        )

    def test_all_employees_have_valid_fk(self, seeded_session):
        """Every employee must reference a valid job_title and department."""
        jt_ids = {
            row[0]
            for row in seeded_session.execute(select(JobTitle.id)).all()
        }
        dept_ids = {
            row[0]
            for row in seeded_session.execute(select(Department.id)).all()
        }

        employees = seeded_session.execute(
            select(Employee.job_title_id, Employee.department_id)
        ).all()

        for jt_id, dept_id in employees:
            assert jt_id in jt_ids, f"Invalid job_title_id: {jt_id}"
            assert dept_id in dept_ids, f"Invalid department_id: {dept_id}"

    def test_salaries_positive(self, seeded_session):
        """All salaries must be positive."""
        min_salary = seeded_session.scalar(select(func.min(Employee.salary)))
        assert min_salary > 0

    def test_employment_types_valid(self, seeded_session):
        """Employment types must be one of the allowed values."""
        valid_types = {"full-time", "part-time", "contract"}
        types = {
            row[0]
            for row in seeded_session.execute(
                select(Employee.employment_type).distinct()
            ).all()
        }
        assert types.issubset(valid_types), (
            f"Invalid employment types: {types - valid_types}"
        )


class TestSeedIdempotency:
    def test_rerun_produces_same_count(self):
        """Running seed twice should still produce exactly 100 rows."""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)

        # Run twice
        seed(count=100, engine=engine)
        seed(count=100, engine=engine)

        Session = sessionmaker(bind=engine)
        session = Session()
        count = session.scalar(select(func.count()).select_from(Employee))
        session.close()
        engine.dispose()

        assert count == 100, f"Expected 100 after re-run, got {count}"


class TestSeedTimingRegressionGuard:
    """8-D.4 — Prevents accidental reversion to row-by-row inserts."""

    def test_seed_completes_under_5_seconds(self):
        """Seeding 100 rows must complete in < 5s (bulk insert guard)."""
        import time

        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)

        start = time.perf_counter()
        seed(count=100, engine=engine)
        elapsed = time.perf_counter() - start

        engine.dispose()

        assert elapsed < 5.0, (
            f"Seed took {elapsed:.1f}s — check for missing transaction batching"
        )

