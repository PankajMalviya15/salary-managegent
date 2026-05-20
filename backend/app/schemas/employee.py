"""
Pydantic schemas for Employee CRUD operations.

Includes validators for salary > 0, 2-char uppercase country,
and hire_date not in the future.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Create ─────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    job_title_id: int = Field(..., gt=0)
    department_id: int = Field(..., gt=0)
    country: str = Field(..., min_length=2, max_length=2)
    salary: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    employment_type: str = Field(default="full-time")
    hire_date: date

    @field_validator("country")
    @classmethod
    def country_must_be_uppercase(cls, v: str) -> str:
        if not v.isupper():
            raise ValueError("Country must be a 2-character uppercase ISO code (e.g. 'US')")
        return v

    @field_validator("hire_date")
    @classmethod
    def hire_date_not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Hire date cannot be in the future")
        return v

    @field_validator("employment_type")
    @classmethod
    def employment_type_valid(cls, v: str) -> str:
        allowed = {"full-time", "part-time", "contract"}
        if v not in allowed:
            raise ValueError(f"Employment type must be one of: {', '.join(sorted(allowed))}")
        return v


# ── Read ───────────────────────────────────────────────────────────

class EmployeeRead(BaseModel):
    id: int
    full_name: str
    email: str
    job_title_id: int
    department_id: int
    job_title: str  # resolved name from relationship
    department: str  # resolved name from relationship
    country: str
    salary: float
    currency: str
    employment_type: str
    hire_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Update (PATCH — all fields optional) ───────────────────────────

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    job_title_id: Optional[int] = Field(default=None, gt=0)
    department_id: Optional[int] = Field(default=None, gt=0)
    country: Optional[str] = Field(default=None, min_length=2, max_length=2)
    salary: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    employment_type: Optional[str] = None
    hire_date: Optional[date] = None

    @field_validator("country")
    @classmethod
    def country_must_be_uppercase(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.isupper():
            raise ValueError("Country must be a 2-character uppercase ISO code")
        return v

    @field_validator("hire_date")
    @classmethod
    def hire_date_not_in_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Hire date cannot be in the future")
        return v

    @field_validator("employment_type")
    @classmethod
    def employment_type_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"full-time", "part-time", "contract"}
            if v not in allowed:
                raise ValueError(f"Employment type must be one of: {', '.join(sorted(allowed))}")
        return v


# ── Paginated Response ─────────────────────────────────────────────

class PaginatedEmployees(BaseModel):
    items: list[EmployeeRead]
    total: int
    next_cursor: Optional[int] = None
