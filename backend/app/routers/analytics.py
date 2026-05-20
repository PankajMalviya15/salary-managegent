"""
Analytics router — endpoints for salary analytics and insights.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import (
    CountrySalarySummary,
    HeadcountByGroup,
    JobTitleSalarySummary,
    OutlierEmployee,
    SalaryDistribution,
)
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/salary-by-country", response_model=list[CountrySalarySummary])
def salary_by_country(db: Session = Depends(get_db)):
    """Get salary statistics (min/max/avg/count) grouped by country."""
    return analytics_service.salary_by_country(db)


@router.get("/salary-by-job-title", response_model=list[JobTitleSalarySummary])
def salary_by_job_title(
    country: Optional[str] = Query(None, description="Filter by country code"),
    db: Session = Depends(get_db),
):
    """Get average salary and count grouped by job title and country."""
    return analytics_service.salary_by_job_title_in_country(db, country=country)


@router.get("/salary-distribution", response_model=SalaryDistribution)
def salary_distribution(
    buckets: int = Query(10, ge=2, le=50, description="Number of histogram buckets"),
    db: Session = Depends(get_db),
):
    """Get salary distribution histogram."""
    return analytics_service.salary_distribution(db, bucket_count=buckets)


@router.get("/headcount", response_model=list[HeadcountByGroup])
def headcount_by_department(db: Session = Depends(get_db)):
    """Get headcount grouped by department."""
    return analytics_service.headcount_by_department(db)


@router.get("/outliers", response_model=list[OutlierEmployee])
def find_outliers(
    threshold: float = Query(2.0, ge=1.0, le=5.0, description="Standard deviation threshold"),
    db: Session = Depends(get_db),
):
    """Find salary outliers (employees > N standard deviations from peer mean)."""
    return analytics_service.find_outliers(db, threshold=threshold)
