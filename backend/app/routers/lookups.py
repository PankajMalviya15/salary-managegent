"""
Lookups router — endpoints for dropdown/filter options.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job_title import JobTitle
from app.models.department import Department
from app.models.employee import Employee

router = APIRouter(prefix="/lookups", tags=["Lookups"])


@router.get("/job-titles")
def list_job_titles(db: Session = Depends(get_db)):
    """Get all job titles for dropdown population."""
    results = db.execute(
        select(JobTitle.id, JobTitle.title).order_by(JobTitle.title)
    ).all()
    return [{"id": row.id, "title": row.title} for row in results]


@router.get("/departments")
def list_departments(db: Session = Depends(get_db)):
    """Get all departments for dropdown population."""
    results = db.execute(
        select(Department.id, Department.name).order_by(Department.name)
    ).all()
    return [{"id": row.id, "name": row.name} for row in results]


@router.get("/countries")
def list_countries(db: Session = Depends(get_db)):
    """Get distinct countries from active employees."""
    results = db.execute(
        select(Employee.country)
        .where(Employee.is_active == True)  # noqa: E712
        .distinct()
        .order_by(Employee.country)
    ).all()
    return [row[0] for row in results]
