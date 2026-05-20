"""
Test analytics API endpoints.

Uses shared conftest fixtures. Seeds a fixed dataset (5 employees
across 2 countries) and verifies each analytics endpoint.
"""

import pytest
from httpx import AsyncClient


class TestSalaryByCountry:
    @pytest.mark.asyncio
    async def test_returns_correct_stats(self, client: AsyncClient, seed_analytics_data):
        resp = await client.get("/api/v1/analytics/salary-by-country")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data) == 2

        us = next(d for d in data if d["country"] == "US")
        assert us["min_salary"] == 80000.0
        assert us["max_salary"] == 120000.0
        assert us["avg_salary"] == 100000.0
        assert us["employee_count"] == 3

        gb = next(d for d in data if d["country"] == "GB")
        assert gb["min_salary"] == 90000.0
        assert gb["max_salary"] == 95000.0
        assert gb["avg_salary"] == 92500.0
        assert gb["employee_count"] == 2


class TestSalaryByJobTitle:
    @pytest.mark.asyncio
    async def test_returns_grouped_data(self, client: AsyncClient, seed_analytics_data):
        resp = await client.get("/api/v1/analytics/salary-by-job-title")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2

    @pytest.mark.asyncio
    async def test_filter_by_country(self, client: AsyncClient, seed_analytics_data):
        resp = await client.get("/api/v1/analytics/salary-by-job-title?country=US")
        assert resp.status_code == 200
        data = resp.json()
        for item in data:
            assert item["country"] == "US"


class TestSalaryDistribution:
    @pytest.mark.asyncio
    async def test_returns_buckets(self, client: AsyncClient, seed_analytics_data):
        resp = await client.get("/api/v1/analytics/salary-distribution")
        assert resp.status_code == 200
        data = resp.json()
        assert "buckets" in data
        assert "total" in data
        assert data["total"] == 5
        assert len(data["buckets"]) == 10


class TestHeadcount:
    @pytest.mark.asyncio
    async def test_returns_department_counts(self, client: AsyncClient, seed_analytics_data):
        resp = await client.get("/api/v1/analytics/headcount")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

        eng = next(d for d in data if d["group"] == "Engineering")
        assert eng["count"] == 3

        ds = next(d for d in data if d["group"] == "Data Science")
        assert ds["count"] == 2


class TestOutliers:
    @pytest.mark.asyncio
    async def test_outlier_detection(self, client: AsyncClient, seed_analytics_data):
        resp = await client.get("/api/v1/analytics/outliers")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
