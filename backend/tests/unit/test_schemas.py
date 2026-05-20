"""
8-A.1 — Pydantic validator unit tests.

Tests every custom validator in EmployeeCreate using parametrize.
No database, no HTTP — pure schema validation.
"""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.employee import EmployeeCreate, EmployeeUpdate


# ── Valid baseline payload ─────────────────────────────────────────

VALID_PAYLOAD = {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "job_title_id": 1,
    "department_id": 1,
    "country": "US",
    "salary": 100_000.0,
    "currency": "USD",
    "employment_type": "full-time",
    "hire_date": date(2024, 1, 15),
}


class TestEmployeeCreateValid:
    """Confirm valid payloads pass without errors."""

    def test_valid_payload_passes(self):
        emp = EmployeeCreate(**VALID_PAYLOAD)
        assert emp.full_name == "Jane Doe"
        assert emp.salary == 100_000.0

    def test_today_hire_date_is_valid(self):
        payload = {**VALID_PAYLOAD, "hire_date": date.today()}
        emp = EmployeeCreate(**payload)
        assert emp.hire_date == date.today()

    def test_valid_country_IN(self):
        payload = {**VALID_PAYLOAD, "country": "IN"}
        emp = EmployeeCreate(**payload)
        assert emp.country == "IN"


class TestEmployeeCreateSalary:
    """Salary must be > 0."""

    @pytest.mark.parametrize(
        "salary,should_fail",
        [
            (0, True),
            (-500, True),
            (0.01, False),
            (1, False),
            (999_999, False),
        ],
        ids=["zero", "negative", "tiny-positive", "one", "large"],
    )
    def test_salary_validation(self, salary, should_fail):
        payload = {**VALID_PAYLOAD, "salary": salary}
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                EmployeeCreate(**payload)
            fields = [e["loc"][-1] for e in exc_info.value.errors()]
            assert "salary" in fields
        else:
            emp = EmployeeCreate(**payload)
            assert emp.salary == salary


class TestEmployeeCreateCountry:
    """Country must be 2-char uppercase ISO code."""

    @pytest.mark.parametrize(
        "country,should_fail",
        [
            ("ind", True),       # 3 chars, lowercase
            ("us", True),        # lowercase
            ("USA", True),       # 3 chars
            ("U", True),         # 1 char
            ("IN", False),       # valid
            ("GB", False),       # valid
        ],
        ids=["3char-lower", "2char-lower", "3char-upper", "1char", "valid-IN", "valid-GB"],
    )
    def test_country_validation(self, country, should_fail):
        payload = {**VALID_PAYLOAD, "country": country}
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                EmployeeCreate(**payload)
            fields = [e["loc"][-1] for e in exc_info.value.errors()]
            assert "country" in fields
        else:
            emp = EmployeeCreate(**payload)
            assert emp.country == country


class TestEmployeeCreateHireDate:
    """Hire date cannot be in the future."""

    @pytest.mark.parametrize(
        "offset_days,should_fail",
        [
            (1, True),        # tomorrow
            (30, True),       # next month
            (0, False),       # today
            (-1, False),      # yesterday
            (-365, False),    # last year
        ],
        ids=["tomorrow", "next-month", "today", "yesterday", "last-year"],
    )
    def test_hire_date_validation(self, offset_days, should_fail):
        hire_date = date.today() + timedelta(days=offset_days)
        payload = {**VALID_PAYLOAD, "hire_date": hire_date}
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                EmployeeCreate(**payload)
            fields = [e["loc"][-1] for e in exc_info.value.errors()]
            assert "hire_date" in fields
        else:
            emp = EmployeeCreate(**payload)
            assert emp.hire_date == hire_date


class TestEmployeeCreateEmail:
    """Email must be valid format."""

    @pytest.mark.parametrize(
        "email,should_fail",
        [
            ("not-an-email", True),
            ("missing-at.com", True),
            ("@nodomain", True),
            ("valid@example.com", False),
            ("user+tag@company.co", False),
        ],
        ids=["no-at", "no-at-v2", "no-local", "valid", "valid-plus"],
    )
    def test_email_validation(self, email, should_fail):
        payload = {**VALID_PAYLOAD, "email": email}
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                EmployeeCreate(**payload)
            fields = [e["loc"][-1] for e in exc_info.value.errors()]
            assert "email" in fields
        else:
            emp = EmployeeCreate(**payload)
            assert emp.email == email


class TestEmployeeCreateEmploymentType:
    """Employment type must be one of the allowed values."""

    @pytest.mark.parametrize(
        "emp_type,should_fail",
        [
            ("freelance", True),
            ("intern", True),
            ("full-time", False),
            ("part-time", False),
            ("contract", False),
        ],
        ids=["freelance", "intern", "full-time", "part-time", "contract"],
    )
    def test_employment_type_validation(self, emp_type, should_fail):
        payload = {**VALID_PAYLOAD, "employment_type": emp_type}
        if should_fail:
            with pytest.raises(ValidationError) as exc_info:
                EmployeeCreate(**payload)
            fields = [e["loc"][-1] for e in exc_info.value.errors()]
            assert "employment_type" in fields
        else:
            emp = EmployeeCreate(**payload)
            assert emp.employment_type == emp_type


class TestEmployeeUpdate:
    """EmployeeUpdate — all fields optional for PATCH."""

    def test_empty_update_is_valid(self):
        update = EmployeeUpdate()
        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_salary_update(self):
        update = EmployeeUpdate(salary=120_000)
        data = update.model_dump(exclude_unset=True)
        assert data == {"salary": 120_000}

    def test_invalid_salary_in_update(self):
        with pytest.raises(ValidationError):
            EmployeeUpdate(salary=-1)

    def test_invalid_country_in_update(self):
        with pytest.raises(ValidationError):
            EmployeeUpdate(country="us")
