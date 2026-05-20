"""
Employee router — CRUD endpoints for employee management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeRead,
    EmployeeUpdate,
    PaginatedEmployees,
)
from app.services import employee_service

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=PaginatedEmployees)
def list_employees(
    cursor: Optional[int] = Query(None, description="Keyset cursor (employee ID)"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    country: Optional[str] = Query(None, description="Filter by 2-char country code"),
    job_title_id: Optional[int] = Query(None, description="Filter by job title ID"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    employment_type: Optional[str] = Query(None, description="Filter by employment type"),
    salary_min: Optional[float] = Query(None, description="Minimum salary filter"),
    salary_max: Optional[float] = Query(None, description="Maximum salary filter"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    """List employees with keyset pagination and optional filters."""
    items, total, next_cursor = employee_service.list_employees(
        db,
        cursor=cursor,
        limit=limit,
        country=country,
        job_title_id=job_title_id,
        department_id=department_id,
        employment_type=employment_type,
        salary_min=salary_min,
        salary_max=salary_max,
        is_active=is_active,
    )
    return PaginatedEmployees(
        items=[
            EmployeeRead(
                **{
                    **{c.key: getattr(emp, c.key) for c in emp.__table__.columns},
                    "job_title": emp.job_title.title,
                    "department": emp.department.name,
                }
            )
            for emp in items
        ],
        total=total,
        next_cursor=next_cursor,
    )


@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
):
    """Create a new employee."""
    emp = employee_service.create_employee(db, data)
    return EmployeeRead(
        **{
            **{c.key: getattr(emp, c.key) for c in emp.__table__.columns},
            "job_title": emp.job_title.title,
            "department": emp.department.name,
        }
    )


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    """Get a single employee by ID."""
    emp = employee_service.get_employee(db, employee_id)
    return EmployeeRead(
        **{
            **{c.key: getattr(emp, c.key) for c in emp.__table__.columns},
            "job_title": emp.job_title.title,
            "department": emp.department.name,
        }
    )


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee_put(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    """Full update of an employee (PUT)."""
    emp = employee_service.update_employee(db, employee_id, data)
    return EmployeeRead(
        **{
            **{c.key: getattr(emp, c.key) for c in emp.__table__.columns},
            "job_title": emp.job_title.title,
            "department": emp.department.name,
        }
    )


@router.patch("/{employee_id}", response_model=EmployeeRead)
def update_employee_patch(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    """Partial update of an employee (PATCH)."""
    emp = employee_service.update_employee(db, employee_id, data)
    return EmployeeRead(
        **{
            **{c.key: getattr(emp, c.key) for c in emp.__table__.columns},
            "job_title": emp.job_title.title,
            "department": emp.department.name,
        }
    )


@router.delete("/{employee_id}", response_model=EmployeeRead)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    """Soft-delete an employee (sets is_active = False)."""
    emp = employee_service.soft_delete_employee(db, employee_id)
    return EmployeeRead(
        **{
            **{c.key: getattr(emp, c.key) for c in emp.__table__.columns},
            "job_title": emp.job_title.title,
            "department": emp.department.name,
        }
    )
