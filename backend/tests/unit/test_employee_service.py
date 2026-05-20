"""
8-A.2 — Service-layer unit tests for employee_service.

Uses a real in-memory SQLite session (fixture, not mock).
Tests each service function in isolation.
"""

from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.job_title import JobTitle
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.employee_service import (
    create_employee,
    get_employee,
    list_employees,
    soft_delete_employee,
    update_employee,
)


# ── In-memory session fixture ─────────────────────────────────────

@pytest.fixture
def mem_session():
    """Fresh in-memory SQLite DB for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _set_fk(dbapi_conn, _):
        dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed lookup tables
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


VALID_CREATE = EmployeeCreate(
    full_name="Alice Smith",
    email="alice@test.com",
    job_title_id=1,
    department_id=1,
    country="US",
    salary=100_000,
    currency="USD",
    employment_type="full-time",
    hire_date=date(2024, 1, 15),
)


class TestCreateEmployee:
    def test_returns_orm_object_with_id_and_created_at(self, mem_session):
        emp = create_employee(mem_session, VALID_CREATE)
        assert emp.id is not None
        assert emp.id > 0
        assert emp.created_at is not None
        assert emp.full_name == "Alice Smith"

    def test_duplicate_email_raises_409(self, mem_session):
        create_employee(mem_session, VALID_CREATE)
        with pytest.raises(HTTPException) as exc_info:
            create_employee(mem_session, VALID_CREATE)
        assert exc_info.value.status_code == 409

    def test_invalid_job_title_raises_422(self, mem_session):
        bad = EmployeeCreate(
            full_name="Bad", email="bad@test.com",
            job_title_id=999, department_id=1,
            country="US", salary=50000, currency="USD",
            employment_type="full-time", hire_date=date(2024, 1, 1),
        )
        with pytest.raises(HTTPException) as exc_info:
            create_employee(mem_session, bad)
        assert exc_info.value.status_code == 422


class TestUpdateEmployee:
    def test_partial_update_changes_only_supplied_fields(self, mem_session):
        emp = create_employee(mem_session, VALID_CREATE)
        original_name = emp.full_name
        original_country = emp.country

        update = EmployeeUpdate(salary=120_000)
        updated = update_employee(mem_session, emp.id, update)

        assert updated.salary == 120_000
        assert updated.full_name == original_name
        assert updated.country == original_country

    def test_empty_update_returns_unchanged(self, mem_session):
        emp = create_employee(mem_session, VALID_CREATE)
        update = EmployeeUpdate()
        updated = update_employee(mem_session, emp.id, update)
        assert updated.salary == emp.salary


class TestSoftDeleteEmployee:
    def test_sets_is_active_false(self, mem_session):
        emp = create_employee(mem_session, VALID_CREATE)
        assert emp.is_active is True

        deleted = soft_delete_employee(mem_session, emp.id)
        assert deleted.is_active is False

    def test_get_employee_still_returns_soft_deleted(self, mem_session):
        emp = create_employee(mem_session, VALID_CREATE)
        soft_delete_employee(mem_session, emp.id)

        # get_employee does NOT filter by is_active — row still exists
        fetched = get_employee(mem_session, emp.id)
        assert fetched.id == emp.id
        assert fetched.is_active is False

    def test_list_employees_excludes_soft_deleted(self, mem_session):
        emp = create_employee(mem_session, VALID_CREATE)
        soft_delete_employee(mem_session, emp.id)

        items, total, _ = list_employees(mem_session, is_active=True)
        ids = [e.id for e in items]
        assert emp.id not in ids


class TestListEmployees:
    def test_returns_active_only_by_default(self, mem_session):
        emp = create_employee(mem_session, VALID_CREATE)
        items, total, _ = list_employees(mem_session)
        assert total >= 1
        assert all(e.is_active for e in items)
