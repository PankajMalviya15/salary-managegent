"""
Test keyset pagination — seed 50 employees, paginate through all,
assert every employee appears exactly once and total matches.
"""

import pytest
from httpx import AsyncClient

from app.models.employee import Employee
from app.models.job_title import JobTitle
from app.models.department import Department
from datetime import date


@pytest.fixture
def seed_50_employees(db_session):
    """Seed 50 employees for pagination tests."""
    db_session.add_all([
        JobTitle(id=1, title="Engineer"),
        Department(id=1, name="Engineering"),
    ])
    db_session.commit()

    employees = [
        Employee(
            full_name=f"Employee {i:03d}",
            email=f"emp{i:03d}@test.com",
            job_title_id=1,
            department_id=1,
            country="US",
            salary=50000 + i * 1000,
            currency="USD",
            employment_type="full-time",
            hire_date=date(2023, 1, 1),
            is_active=True,
        )
        for i in range(50)
    ]
    db_session.add_all(employees)
    db_session.commit()


class TestKeysetPagination:
    @pytest.mark.asyncio
    async def test_paginate_all_pages(self, client: AsyncClient, seed_50_employees):
        """Walk through all pages using next_cursor, collect every ID."""
        all_ids: list[int] = []
        cursor = None
        page_count = 0
        limit = 10

        while True:
            url = f"/api/v1/employees?limit={limit}"
            if cursor:
                url += f"&cursor={cursor}"

            resp = await client.get(url)
            assert resp.status_code == 200
            data = resp.json()

            assert data["total"] == 50

            items = data["items"]
            all_ids.extend(item["id"] for item in items)
            page_count += 1

            cursor = data["next_cursor"]
            if cursor is None:
                break

        # Every employee appears exactly once
        assert len(all_ids) == 50
        assert len(set(all_ids)) == 50

        # We expect 5 pages of 10
        assert page_count == 5

    @pytest.mark.asyncio
    async def test_ids_are_ascending(self, client: AsyncClient, seed_50_employees):
        """IDs within each page should be in ascending order."""
        resp = await client.get("/api/v1/employees?limit=20")
        items = resp.json()["items"]
        ids = [item["id"] for item in items]
        assert ids == sorted(ids)

    @pytest.mark.asyncio
    async def test_cursor_beyond_last_returns_empty(self, client: AsyncClient, seed_50_employees):
        """Using a cursor beyond the last ID returns no items."""
        resp = await client.get("/api/v1/employees?cursor=999999&limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 0
        assert data["next_cursor"] is None

    @pytest.mark.asyncio
    async def test_limit_boundary(self, client: AsyncClient, seed_50_employees):
        """Limit=50 returns all employees in one page with no next_cursor."""
        resp = await client.get("/api/v1/employees?limit=50")
        data = resp.json()
        assert len(data["items"]) == 50
        assert data["next_cursor"] is None

    @pytest.mark.asyncio
    async def test_limit_exceeds_total(self, client: AsyncClient, seed_50_employees):
        """Limit>total returns all employees with no next_cursor."""
        resp = await client.get("/api/v1/employees?limit=100")
        data = resp.json()
        assert len(data["items"]) == 50
        assert data["next_cursor"] is None
