"""
Test filtering — country, job_title, combined filters, salary range.
"""

import pytest
from httpx import AsyncClient

from app.models.employee import Employee
from app.models.job_title import JobTitle
from app.models.department import Department
from datetime import date


@pytest.fixture
def seed_filter_data(db_session):
    """Seed employees for filter testing."""
    jt1 = JobTitle(id=1, title="Engineer")
    jt2 = JobTitle(id=2, title="Designer")
    dept = Department(id=1, name="Product")
    db_session.add_all([jt1, jt2, dept])
    db_session.commit()

    employees = [
        # US Engineers
        Employee(full_name="US Eng 1", email="us_eng1@t.com", job_title_id=1,
                 department_id=1, country="US", salary=100000, currency="USD",
                 employment_type="full-time", hire_date=date(2023, 1, 1), is_active=True),
        Employee(full_name="US Eng 2", email="us_eng2@t.com", job_title_id=1,
                 department_id=1, country="US", salary=120000, currency="USD",
                 employment_type="full-time", hire_date=date(2023, 6, 1), is_active=True),
        # US Designer
        Employee(full_name="US Des 1", email="us_des1@t.com", job_title_id=2,
                 department_id=1, country="US", salary=90000, currency="USD",
                 employment_type="contract", hire_date=date(2024, 1, 1), is_active=True),
        # GB Engineer
        Employee(full_name="GB Eng 1", email="gb_eng1@t.com", job_title_id=1,
                 department_id=1, country="GB", salary=80000, currency="GBP",
                 employment_type="full-time", hire_date=date(2023, 3, 1), is_active=True),
        # GB Designer (inactive)
        Employee(full_name="GB Des 1", email="gb_des1@t.com", job_title_id=2,
                 department_id=1, country="GB", salary=75000, currency="GBP",
                 employment_type="part-time", hire_date=date(2024, 2, 1), is_active=False),
    ]
    db_session.add_all(employees)
    db_session.commit()


class TestCountryFilter:
    @pytest.mark.asyncio
    async def test_filter_by_country_us(self, client: AsyncClient, seed_filter_data):
        resp = await client.get("/api/v1/employees?country=US")
        data = resp.json()
        assert data["total"] == 3
        for item in data["items"]:
            assert item["country"] == "US"

    @pytest.mark.asyncio
    async def test_filter_by_country_gb(self, client: AsyncClient, seed_filter_data):
        resp = await client.get("/api/v1/employees?country=GB")
        data = resp.json()
        # Only 1 active GB employee (the other is inactive)
        assert data["total"] == 1
        assert data["items"][0]["country"] == "GB"

    @pytest.mark.asyncio
    async def test_filter_nonexistent_country(self, client: AsyncClient, seed_filter_data):
        resp = await client.get("/api/v1/employees?country=ZZ")
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestJobTitleFilter:
    @pytest.mark.asyncio
    async def test_filter_by_job_title(self, client: AsyncClient, seed_filter_data):
        resp = await client.get("/api/v1/employees?job_title_id=1")
        data = resp.json()
        # 3 active engineers (2 US + 1 GB)
        assert data["total"] == 3
        for item in data["items"]:
            assert item["job_title"] == "Engineer"


class TestCombinedFilters:
    @pytest.mark.asyncio
    async def test_country_plus_job_title(self, client: AsyncClient, seed_filter_data):
        """Combined filters return intersection."""
        resp = await client.get("/api/v1/employees?country=US&job_title_id=1")
        data = resp.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["country"] == "US"
            assert item["job_title"] == "Engineer"

    @pytest.mark.asyncio
    async def test_country_plus_employment_type(self, client: AsyncClient, seed_filter_data):
        resp = await client.get("/api/v1/employees?country=US&employment_type=contract")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["employment_type"] == "contract"


class TestSalaryRangeFilter:
    @pytest.mark.asyncio
    async def test_salary_min(self, client: AsyncClient, seed_filter_data):
        resp = await client.get("/api/v1/employees?salary_min=100000")
        data = resp.json()
        for item in data["items"]:
            assert item["salary"] >= 100000

    @pytest.mark.asyncio
    async def test_salary_max(self, client: AsyncClient, seed_filter_data):
        resp = await client.get("/api/v1/employees?salary_max=90000")
        data = resp.json()
        for item in data["items"]:
            assert item["salary"] <= 90000

    @pytest.mark.asyncio
    async def test_salary_range(self, client: AsyncClient, seed_filter_data):
        resp = await client.get("/api/v1/employees?salary_min=85000&salary_max=105000")
        data = resp.json()
        for item in data["items"]:
            assert 85000 <= item["salary"] <= 105000

    @pytest.mark.asyncio
    async def test_salary_exact_boundary(self, client: AsyncClient, seed_filter_data):
        """Boundary: salary_min=100000&salary_max=100000 should match exact salary."""
        resp = await client.get("/api/v1/employees?salary_min=100000&salary_max=100000")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["salary"] == 100000


class TestActiveFilter:
    @pytest.mark.asyncio
    async def test_include_inactive(self, client: AsyncClient, seed_filter_data):
        """is_active=false returns only inactive employees."""
        resp = await client.get("/api/v1/employees?is_active=false")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["is_active"] is False
