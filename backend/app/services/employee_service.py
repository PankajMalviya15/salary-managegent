"""
Employee service — business logic for employee CRUD.

All functions accept a SQLAlchemy Session and return ORM objects
or raise HTTPException on errors.
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.employee import Employee
from app.models.job_title import JobTitle
from app.models.department import Department
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def list_employees(
    db: Session,
    *,
    cursor: Optional[int] = None,
    limit: int = 20,
    country: Optional[str] = None,
    job_title_id: Optional[int] = None,
    department_id: Optional[int] = None,
    employment_type: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    is_active: Optional[bool] = True,
) -> tuple[list[Employee], int, Optional[int]]:
    """
    List employees with keyset pagination and multi-filter support.

    Returns (items, total_count, next_cursor).
    """
    # Base query with eager-loaded relationships
    query = select(Employee).options(
        joinedload(Employee.job_title),
        joinedload(Employee.department),
    )

    # Apply filters
    if is_active is not None:
        query = query.where(Employee.is_active == is_active)
    if country:
        query = query.where(Employee.country == country)
    if job_title_id:
        query = query.where(Employee.job_title_id == job_title_id)
    if department_id:
        query = query.where(Employee.department_id == department_id)
    if employment_type:
        query = query.where(Employee.employment_type == employment_type)
    if salary_min is not None:
        query = query.where(Employee.salary >= salary_min)
    if salary_max is not None:
        query = query.where(Employee.salary <= salary_max)

    # Count total (before pagination)
    count_query = select(func.count()).select_from(Employee)
    if is_active is not None:
        count_query = count_query.where(Employee.is_active == is_active)
    if country:
        count_query = count_query.where(Employee.country == country)
    if job_title_id:
        count_query = count_query.where(Employee.job_title_id == job_title_id)
    if department_id:
        count_query = count_query.where(Employee.department_id == department_id)
    if employment_type:
        count_query = count_query.where(Employee.employment_type == employment_type)
    if salary_min is not None:
        count_query = count_query.where(Employee.salary >= salary_min)
    if salary_max is not None:
        count_query = count_query.where(Employee.salary <= salary_max)

    total = db.scalar(count_query) or 0

    # Keyset pagination
    if cursor:
        query = query.where(Employee.id > cursor)

    query = query.order_by(Employee.id).limit(limit + 1)

    results = list(db.scalars(query).unique())

    # Determine next cursor
    next_cursor = None
    if len(results) > limit:
        results = results[:limit]
        next_cursor = results[-1].id

    return results, total, next_cursor


def get_employee(db: Session, employee_id: int) -> Employee:
    """Get a single employee by ID. Raises 404 if not found."""
    employee = db.scalar(
        select(Employee)
        .options(
            joinedload(Employee.job_title),
            joinedload(Employee.department),
        )
        .where(Employee.id == employee_id)
    )
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found",
        )
    return employee


def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    """Create a new employee. Raises 409 on duplicate email, 422 on invalid FK."""
    # Validate FKs exist
    if not db.scalar(select(JobTitle).where(JobTitle.id == data.job_title_id)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Job title with id {data.job_title_id} not found",
        )
    if not db.scalar(select(Department).where(Department.id == data.department_id)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Department with id {data.department_id} not found",
        )

    employee = Employee(**data.model_dump())
    db.add(employee)
    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An employee with email '{data.email}' already exists",
        )

    # Eager load relationships for the response
    return get_employee(db, employee.id)


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> Employee:
    """
    Update an employee with merge-patch semantics.
    Only fields present in the request body are updated.
    """
    employee = get_employee(db, employee_id)

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return employee

    for field, value in update_data.items():
        setattr(employee, field, value)

    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Update would create a duplicate email",
        )

    return get_employee(db, employee.id)


def soft_delete_employee(db: Session, employee_id: int) -> Employee:
    """Soft-delete an employee by setting is_active = False."""
    employee = get_employee(db, employee_id)

    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found",
        )

    employee.is_active = False
    db.commit()
    db.refresh(employee)
    return employee
