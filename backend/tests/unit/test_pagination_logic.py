"""
8-A.4 — Keyset pagination unit tests.

Seeds 7 employees in-memory with known IDs.
Paginates with page size 3 and verifies cursor behaviour.
"""

from datetime import date

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.job_title import JobTitle
from app.models.department import Department
from app.models.employee import Employee
from app.services.employee_service import list_employees


@pytest.fixture
def pagination_session():
    """In-memory DB with 7 employees for pagination tests."""
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
        Department(id=1, name="Engineering"),
    ])
    session.commit()

    # 7 employees
    for i in range(1, 8):
        session.add(Employee(
            full_name=f"Employee {i}",
            email=f"emp{i}@test.com",
            job_title_id=1,
            department_id=1,
            country="US",
            salary=50_000 + i * 10_000,
            currency="USD",
            employment_type="full-time",
            hire_date=date(2024, 1, i),
            is_active=True,
        ))
    session.commit()

    yield session
    session.close()
    engine.dispose()


class TestKeysetPagination:
    def test_page1_returns_3_rows_with_cursor(self, pagination_session):
        items, total, next_cursor = list_employees(
            pagination_session, limit=3
        )
        assert len(items) == 3
        assert total == 7
        assert next_cursor is not None
        assert next_cursor == items[-1].id

    def test_page2_returns_3_rows(self, pagination_session):
        # Get page 1
        items1, _, cursor1 = list_employees(pagination_session, limit=3)
        assert cursor1 is not None

        # Get page 2
        items2, total, cursor2 = list_employees(
            pagination_session, cursor=cursor1, limit=3
        )
        assert len(items2) == 3
        assert total == 7
        assert cursor2 is not None

    def test_page3_returns_1_row_with_null_cursor(self, pagination_session):
        # Page 1
        _, _, cursor1 = list_employees(pagination_session, limit=3)
        # Page 2
        _, _, cursor2 = list_employees(pagination_session, cursor=cursor1, limit=3)
        # Page 3
        items3, total, cursor3 = list_employees(
            pagination_session, cursor=cursor2, limit=3
        )
        assert len(items3) == 1
        assert total == 7
        assert cursor3 is None

    def test_all_pages_cover_all_employees_no_duplicates(self, pagination_session):
        all_ids = []
        cursor = None
        page_count = 0

        while True:
            items, total, next_cursor = list_employees(
                pagination_session, cursor=cursor, limit=3
            )
            all_ids.extend(e.id for e in items)
            cursor = next_cursor
            page_count += 1
            if next_cursor is None:
                break

        assert page_count == 3
        assert len(all_ids) == 7
        assert len(set(all_ids)) == 7  # no duplicates

    def test_ids_are_ascending_across_pages(self, pagination_session):
        all_ids = []
        cursor = None

        while True:
            items, _, next_cursor = list_employees(
                pagination_session, cursor=cursor, limit=3
            )
            all_ids.extend(e.id for e in items)
            cursor = next_cursor
            if next_cursor is None:
                break

        assert all_ids == sorted(all_ids)
