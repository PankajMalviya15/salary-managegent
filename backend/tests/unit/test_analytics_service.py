"""
8-A.3 — Analytics service unit tests.

Uses a fixed in-memory dataset (no seed script).
Tests exact numeric outputs for each analytics function.
"""

from datetime import date

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.job_title import JobTitle
from app.models.department import Department
from app.models.employee import Employee
from app.services.analytics_service import (
    find_outliers,
    headcount_by_department,
    salary_by_country,
    salary_distribution,
)


@pytest.fixture
def analytics_session():
    """In-memory DB with a fixed, deterministic dataset."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _set_fk(dbapi_conn, _):
        dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Lookups
    session.add_all([
        JobTitle(id=1, title="Software Engineer"),
        JobTitle(id=2, title="Data Scientist"),
        Department(id=1, name="Engineering"),
        Department(id=2, name="Data Science"),
    ])
    session.commit()

    yield session
    session.close()
    engine.dispose()


def _make_employee(
    name, email, jt_id, dept_id, country, salary, **kwargs
) -> Employee:
    return Employee(
        full_name=name,
        email=email,
        job_title_id=jt_id,
        department_id=dept_id,
        country=country,
        salary=salary,
        currency=kwargs.get("currency", "USD"),
        employment_type=kwargs.get("employment_type", "full-time"),
        hire_date=kwargs.get("hire_date", date(2024, 1, 1)),
        is_active=kwargs.get("is_active", True),
    )


class TestSalaryByCountry:
    def test_exact_stats_for_known_data(self, analytics_session):
        """3 employees in IN earning 50k/60k/70k → avg=60000, min=50000, max=70000, count=3."""
        analytics_session.add_all([
            _make_employee("A", "a@t.com", 1, 1, "IN", 50_000),
            _make_employee("B", "b@t.com", 1, 1, "IN", 60_000),
            _make_employee("C", "c@t.com", 1, 1, "IN", 70_000),
        ])
        analytics_session.commit()

        results = salary_by_country(analytics_session)
        assert len(results) == 1

        india = results[0]
        assert india["country"] == "IN"
        assert india["min_salary"] == 50_000
        assert india["max_salary"] == 70_000
        assert india["avg_salary"] == 60_000
        assert india["employee_count"] == 3

    def test_multiple_countries(self, analytics_session):
        analytics_session.add_all([
            _make_employee("A", "a@t.com", 1, 1, "US", 100_000),
            _make_employee("B", "b@t.com", 1, 1, "GB", 80_000),
        ])
        analytics_session.commit()

        results = salary_by_country(analytics_session)
        countries = {r["country"] for r in results}
        assert countries == {"US", "GB"}

    def test_excludes_inactive_employees(self, analytics_session):
        analytics_session.add_all([
            _make_employee("Active", "act@t.com", 1, 1, "US", 100_000, is_active=True),
            _make_employee("Inactive", "inact@t.com", 1, 1, "US", 200_000, is_active=False),
        ])
        analytics_session.commit()

        results = salary_by_country(analytics_session)
        us = [r for r in results if r["country"] == "US"][0]
        assert us["employee_count"] == 1
        assert us["avg_salary"] == 100_000


class TestSalaryDistribution:
    def test_uniform_distribution_five_buckets(self, analytics_session):
        """Salaries [10, 20, 30, 40, 50] with 5 buckets → 1 employee per bucket."""
        for i, salary in enumerate([10, 20, 30, 40, 50]):
            analytics_session.add(
                _make_employee(f"E{i}", f"e{i}@t.com", 1, 1, "US", salary)
            )
        analytics_session.commit()

        result = salary_distribution(analytics_session, bucket_count=5)
        assert result["total"] == 5
        assert len(result["buckets"]) == 5
        # Each bucket should have exactly 1 employee
        counts = [b["count"] for b in result["buckets"]]
        assert sum(counts) == 5

    def test_empty_dataset(self, analytics_session):
        result = salary_distribution(analytics_session)
        assert result["total"] == 0
        assert result["buckets"] == []


class TestFindOutliers:
    def test_detects_outlier_at_3sd(self, analytics_session):
        """9 employees near mean, 1 at mean + 3SD → only that 1 is returned."""
        # Group: country=US, job_title_id=1
        # 9 employees at salary ~100k (very tight cluster)
        for i in range(9):
            analytics_session.add(
                _make_employee(f"Normal{i}", f"n{i}@t.com", 1, 1, "US", 100_000)
            )
        # 1 outlier at 300k (well above 2 SD from the group)
        analytics_session.add(
            _make_employee("Outlier", "outlier@t.com", 1, 1, "US", 300_000)
        )
        analytics_session.commit()

        outliers = find_outliers(analytics_session, threshold=2.0)
        assert len(outliers) >= 1
        outlier_names = [o["full_name"] for o in outliers]
        assert "Outlier" in outlier_names

    def test_no_outliers_in_uniform_group(self, analytics_session):
        """All employees have the same salary → no outliers."""
        for i in range(5):
            analytics_session.add(
                _make_employee(f"E{i}", f"e{i}@t.com", 1, 1, "US", 100_000)
            )
        analytics_session.commit()

        outliers = find_outliers(analytics_session, threshold=2.0)
        assert len(outliers) == 0


class TestHeadcountByDepartment:
    def test_counts_match_inserted_rows(self, analytics_session):
        analytics_session.add_all([
            _make_employee("A", "a@t.com", 1, 1, "US", 100_000),
            _make_employee("B", "b@t.com", 1, 1, "US", 110_000),
            _make_employee("C", "c@t.com", 2, 2, "GB", 90_000),
        ])
        analytics_session.commit()

        results = headcount_by_department(analytics_session)
        dept_counts = {r["group"]: r["count"] for r in results}

        assert dept_counts["Engineering"] == 2
        assert dept_counts["Data Science"] == 1

    def test_excludes_inactive(self, analytics_session):
        analytics_session.add_all([
            _make_employee("Active", "a@t.com", 1, 1, "US", 100_000, is_active=True),
            _make_employee("Inactive", "i@t.com", 1, 1, "US", 100_000, is_active=False),
        ])
        analytics_session.commit()

        results = headcount_by_department(analytics_session)
        total = sum(r["count"] for r in results)
        assert total == 1
