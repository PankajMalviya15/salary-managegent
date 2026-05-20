"""
Test employee API endpoints.

Uses shared conftest fixtures for DB setup and async client.
Tests the full create → read → update → soft delete lifecycle.
"""

import pytest
from httpx import AsyncClient


VALID_EMPLOYEE = {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "job_title_id": 1,
    "department_id": 1,
    "country": "US",
    "salary": 100000.0,
    "currency": "USD",
    "employment_type": "full-time",
    "hire_date": "2024-01-15",
}


class TestEmployeeCRUDLifecycle:
    @pytest.mark.asyncio
    async def test_create_employee(self, client: AsyncClient, seed_lookups):
        resp = await client.post("/api/v1/employees", json=VALID_EMPLOYEE)
        assert resp.status_code == 201
        data = resp.json()
        assert data["full_name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["job_title"] == "Software Engineer"
        assert data["department"] == "Engineering"
        assert data["is_active"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_read_employee(self, client: AsyncClient, seed_lookups):
        create_resp = await client.post("/api/v1/employees", json=VALID_EMPLOYEE)
        emp_id = create_resp.json()["id"]

        resp = await client.get(f"/api/v1/employees/{emp_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == emp_id
        assert resp.json()["full_name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_update_employee(self, client: AsyncClient, seed_lookups):
        create_resp = await client.post("/api/v1/employees", json=VALID_EMPLOYEE)
        emp_id = create_resp.json()["id"]

        resp = await client.patch(
            f"/api/v1/employees/{emp_id}",
            json={"salary": 120000.0},
        )
        assert resp.status_code == 200
        assert resp.json()["salary"] == 120000.0
        assert resp.json()["full_name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_soft_delete_employee(self, client: AsyncClient, seed_lookups):
        create_resp = await client.post("/api/v1/employees", json=VALID_EMPLOYEE)
        emp_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/v1/employees/{emp_id}")
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_get_after_soft_delete_still_accessible(self, client: AsyncClient, seed_lookups):
        create_resp = await client.post("/api/v1/employees", json=VALID_EMPLOYEE)
        emp_id = create_resp.json()["id"]
        await client.delete(f"/api/v1/employees/{emp_id}")

        resp = await client.get(f"/api/v1/employees/{emp_id}")
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False


class TestEmployeeValidation:
    @pytest.mark.asyncio
    async def test_negative_salary_returns_422(self, client: AsyncClient, seed_lookups):
        bad_data = {**VALID_EMPLOYEE, "salary": -5000}
        resp = await client.post("/api/v1/employees", json=bad_data)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_country_returns_422(self, client: AsyncClient, seed_lookups):
        bad_data = {**VALID_EMPLOYEE, "country": "usa", "email": "x@x.com"}
        resp = await client.post("/api/v1/employees", json=bad_data)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_future_hire_date_returns_422(self, client: AsyncClient, seed_lookups):
        bad_data = {**VALID_EMPLOYEE, "hire_date": "2099-12-31", "email": "y@y.com"}
        resp = await client.post("/api/v1/employees", json=bad_data)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_not_found_returns_404(self, client: AsyncClient, seed_lookups):
        resp = await client.get("/api/v1/employees/99999")
        assert resp.status_code == 404


class TestEmployeeList:
    @pytest.mark.asyncio
    async def test_list_employees_empty(self, client: AsyncClient, seed_lookups):
        resp = await client.get("/api/v1/employees")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_with_filter(self, client: AsyncClient, seed_lookups):
        emp1 = {**VALID_EMPLOYEE, "country": "US", "email": "a@a.com"}
        emp2 = {**VALID_EMPLOYEE, "country": "GB", "email": "b@b.com"}
        await client.post("/api/v1/employees", json=emp1)
        await client.post("/api/v1/employees", json=emp2)

        resp = await client.get("/api/v1/employees?country=US")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["country"] == "US"
