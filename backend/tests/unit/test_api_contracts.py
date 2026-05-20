"""
8-A.6 — API contract smoke tests.

Uses FastAPI's TestClient (sync) to verify every route exists,
returns correct status codes, and validates request bodies.
No real server — TestClient calls the ASGI app in-process.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.job_title import JobTitle
from app.models.department import Department
from app.models.employee import Employee


# ── Test DB + dependency override ──────────────────────────────────

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})


@event.listens_for(_engine, "connect")
def _set_fk(dbapi_conn, _):
    dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")


_TestSession = sessionmaker(bind=_engine)


def _override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Create/drop all tables for each test."""
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def seed_data():
    """Seed lookups and one employee for contract tests."""
    session = _TestSession()
    session.add_all([
        JobTitle(id=1, title="Software Engineer"),
        Department(id=1, name="Engineering"),
    ])
    session.commit()
    session.close()


VALID_EMPLOYEE = {
    "full_name": "Test User",
    "email": "test@example.com",
    "job_title_id": 1,
    "department_id": 1,
    "country": "US",
    "salary": 100000,
    "currency": "USD",
    "employment_type": "full-time",
    "hire_date": "2024-01-15",
}


class TestHealthEndpoint:
    def test_health_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestEmployeeRoutes:
    def test_list_employees_returns_200(self, seed_data):
        resp = client.get("/api/v1/employees")
        assert resp.status_code == 200
        assert "items" in resp.json()
        assert "total" in resp.json()

    def test_create_employee_returns_201(self, seed_data):
        resp = client.post("/api/v1/employees", json=VALID_EMPLOYEE)
        assert resp.status_code == 201
        assert resp.json()["full_name"] == "Test User"

    def test_get_employee_returns_200(self, seed_data):
        # Create first
        create_resp = client.post("/api/v1/employees", json=VALID_EMPLOYEE)
        emp_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/employees/{emp_id}")
        assert resp.status_code == 200

    def test_delete_nonexistent_returns_404(self, seed_data):
        resp = client.delete("/api/v1/employees/99999")
        assert resp.status_code == 404

    def test_malformed_create_returns_422(self, seed_data):
        bad_payload = {**VALID_EMPLOYEE, "salary": -100}
        resp = client.post("/api/v1/employees", json=bad_payload)
        assert resp.status_code == 422
        body = resp.json()
        # Pydantic validation error should contain the offending field
        assert "detail" in body
        field_names = [err.get("loc", [""])[-1] for err in body["detail"]]
        assert "salary" in field_names

    def test_invalid_country_returns_422(self, seed_data):
        bad_payload = {**VALID_EMPLOYEE, "country": "usa", "email": "x@y.com"}
        resp = client.post("/api/v1/employees", json=bad_payload)
        assert resp.status_code == 422


class TestAnalyticsRoutes:
    def test_salary_by_country_returns_200(self, seed_data):
        resp = client.get("/api/v1/analytics/salary-by-country")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_salary_by_job_title_returns_200(self, seed_data):
        resp = client.get("/api/v1/analytics/salary-by-job-title")
        assert resp.status_code == 200

    def test_salary_distribution_returns_200(self, seed_data):
        resp = client.get("/api/v1/analytics/salary-distribution")
        assert resp.status_code == 200
        assert "buckets" in resp.json()

    def test_headcount_returns_200(self, seed_data):
        resp = client.get("/api/v1/analytics/headcount")
        assert resp.status_code == 200

    def test_outliers_returns_200(self, seed_data):
        resp = client.get("/api/v1/analytics/outliers")
        assert resp.status_code == 200


class TestLookupRoutes:
    def test_job_titles_returns_200(self, seed_data):
        resp = client.get("/api/v1/lookups/job-titles")
        assert resp.status_code == 200

    def test_departments_returns_200(self, seed_data):
        resp = client.get("/api/v1/lookups/departments")
        assert resp.status_code == 200

    def test_countries_returns_200(self, seed_data):
        resp = client.get("/api/v1/lookups/countries")
        assert resp.status_code == 200
