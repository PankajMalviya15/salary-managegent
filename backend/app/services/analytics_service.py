"""
Analytics service — business logic for salary analytics.

All functions accept a SQLAlchemy Session and return data structures
matching the analytics schemas.
"""

import math
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.job_title import JobTitle
from app.models.department import Department


def salary_by_country(db: Session, is_active: bool = True) -> list[dict]:
    """MIN/MAX/AVG salary and COUNT grouped by country."""
    query = (
        select(
            Employee.country,
            func.min(Employee.salary).label("min_salary"),
            func.max(Employee.salary).label("max_salary"),
            func.avg(Employee.salary).label("avg_salary"),
            func.count(Employee.id).label("employee_count"),
        )
        .where(Employee.is_active == is_active)
        .group_by(Employee.country)
        .order_by(func.avg(Employee.salary).desc())
    )

    results = db.execute(query).all()
    return [
        {
            "country": row.country,
            "min_salary": round(row.min_salary, 2),
            "max_salary": round(row.max_salary, 2),
            "avg_salary": round(row.avg_salary, 2),
            "employee_count": row.employee_count,
        }
        for row in results
    ]


def salary_by_job_title_in_country(
    db: Session,
    country: str | None = None,
    is_active: bool = True,
) -> list[dict]:
    """AVG salary and COUNT grouped by job title + country."""
    query = (
        select(
            JobTitle.title.label("job_title"),
            Employee.country,
            func.avg(Employee.salary).label("avg_salary"),
            func.count(Employee.id).label("employee_count"),
        )
        .join(JobTitle, Employee.job_title_id == JobTitle.id)
        .where(Employee.is_active == is_active)
        .group_by(JobTitle.title, Employee.country)
        .order_by(func.avg(Employee.salary).desc())
    )

    if country:
        query = query.where(Employee.country == country)

    results = db.execute(query).all()
    return [
        {
            "job_title": row.job_title,
            "country": row.country,
            "avg_salary": round(row.avg_salary, 2),
            "employee_count": row.employee_count,
        }
        for row in results
    ]


def salary_distribution(
    db: Session,
    bucket_count: int = 10,
    is_active: bool = True,
) -> dict:
    """
    Histogram of salary distribution.
    Computes bucket boundaries from min/max salary and counts employees in each.
    """
    salaries_query = (
        select(Employee.salary)
        .where(Employee.is_active == is_active)
    )
    salaries = [row[0] for row in db.execute(salaries_query).all()]

    if not salaries:
        return {"buckets": [], "total": 0}

    min_sal = min(salaries)
    max_sal = max(salaries)
    bucket_width = (max_sal - min_sal) / bucket_count if max_sal != min_sal else 1

    buckets = []
    for i in range(bucket_count):
        bucket_min = min_sal + i * bucket_width
        bucket_max = min_sal + (i + 1) * bucket_width
        count = sum(
            1
            for s in salaries
            if (bucket_min <= s < bucket_max) or (i == bucket_count - 1 and s == bucket_max)
        )
        buckets.append(
            {
                "bucket_min": round(bucket_min, 2),
                "bucket_max": round(bucket_max, 2),
                "count": count,
            }
        )

    return {"buckets": buckets, "total": len(salaries)}


def headcount_by_department(db: Session, is_active: bool = True) -> list[dict]:
    """Headcount grouped by department."""
    query = (
        select(
            Department.name.label("group"),
            func.count(Employee.id).label("count"),
        )
        .join(Department, Employee.department_id == Department.id)
        .where(Employee.is_active == is_active)
        .group_by(Department.name)
        .order_by(func.count(Employee.id).desc())
    )

    results = db.execute(query).all()
    return [{"group": row.group, "count": row.count} for row in results]


def find_outliers(db: Session, threshold: float = 2.0, is_active: bool = True) -> list[dict]:
    """
    Find employees whose salary is > `threshold` standard deviations
    from their country + job_title peer group mean.
    """
    # Get all active employees with relationships
    query = (
        select(
            Employee.id,
            Employee.full_name,
            Employee.email,
            JobTitle.title.label("job_title"),
            Employee.country,
            Employee.salary,
            Employee.job_title_id,
        )
        .join(JobTitle, Employee.job_title_id == JobTitle.id)
        .where(Employee.is_active == is_active)
    )
    employees = db.execute(query).all()

    # Group salaries by (country, job_title_id)
    groups: dict[tuple, list[float]] = defaultdict(list)
    for emp in employees:
        key = (emp.country, emp.job_title_id)
        groups[key].append(emp.salary)

    # Compute mean and std for each group
    group_stats: dict[tuple, tuple[float, float]] = {}
    for key, salaries in groups.items():
        n = len(salaries)
        if n < 2:
            continue
        mean = sum(salaries) / n
        variance = sum((s - mean) ** 2 for s in salaries) / n
        std = math.sqrt(variance)
        if std > 0:
            group_stats[key] = (mean, std)

    # Find outliers
    outliers = []
    for emp in employees:
        key = (emp.country, emp.job_title_id)
        if key not in group_stats:
            continue
        mean, std = group_stats[key]
        deviation = (emp.salary - mean) / std
        if abs(deviation) > threshold:
            outliers.append(
                {
                    "id": emp.id,
                    "full_name": emp.full_name,
                    "email": emp.email,
                    "job_title": emp.job_title,
                    "country": emp.country,
                    "salary": round(emp.salary, 2),
                    "peer_mean": round(mean, 2),
                    "peer_std": round(std, 2),
                    "deviation": round(deviation, 2),
                }
            )

    # Sort by absolute deviation descending
    outliers.sort(key=lambda x: abs(x["deviation"]), reverse=True)
    return outliers
