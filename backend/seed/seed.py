"""
Seed script — populates the database with deterministic sample data.

Usage:
    python -m seed.seed               # seeds 10,000 employees (default)
    python -m seed.seed --count 100   # seeds 100 employees (dev mode)

Features:
    - Deterministic output via random.Random(42)
    - Fast bulk insert in a single transaction
    - Idempotent: truncates tables on every run
    - CLI --count argument for flexible seeding
    - Timing benchmark output
"""

import argparse
import os
import sys
from datetime import date, timedelta
import time
from pathlib import Path
from random import Random

from dotenv import load_dotenv
from sqlalchemy import create_engine, delete, insert, text
from sqlalchemy.orm import sessionmaker

# ── Ensure backend root is on sys.path ─────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

load_dotenv()

from app.database import Base  # noqa: E402
from app.models.job_title import JobTitle  # noqa: E402
from app.models.department import Department  # noqa: E402
from app.models.employee import Employee  # noqa: E402


# ── Constants ──────────────────────────────────────────────────────

COUNTRIES = ["US", "GB", "DE", "IN", "CA", "AU", "FR", "JP", "BR", "SG"]

JOB_TITLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Staff Engineer",
    "Engineering Manager",
    "Product Manager",
    "Data Scientist",
    "Data Analyst",
    "UX Designer",
    "DevOps Engineer",
    "QA Engineer",
    "Technical Writer",
    "Solutions Architect",
    "Business Analyst",
    "Project Manager",
    "HR Specialist",
]

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Data Science",
    "Design",
    "DevOps",
    "Quality Assurance",
    "Marketing",
    "Human Resources",
    "Finance",
    "Operations",
]

# Salary ranges (min, max) in USD, keyed by job title
SALARY_RANGES: dict[str, tuple[int, int]] = {
    "Software Engineer":        (70_000, 130_000),
    "Senior Software Engineer": (110_000, 180_000),
    "Staff Engineer":           (150_000, 250_000),
    "Engineering Manager":      (140_000, 230_000),
    "Product Manager":          (100_000, 180_000),
    "Data Scientist":           (90_000, 170_000),
    "Data Analyst":             (60_000, 110_000),
    "UX Designer":              (75_000, 140_000),
    "DevOps Engineer":          (85_000, 160_000),
    "QA Engineer":              (65_000, 120_000),
    "Technical Writer":         (60_000, 110_000),
    "Solutions Architect":      (130_000, 220_000),
    "Business Analyst":         (65_000, 125_000),
    "Project Manager":          (80_000, 150_000),
    "HR Specialist":            (50_000, 95_000),
}

CURRENCY_BY_COUNTRY: dict[str, str] = {
    "US": "USD", "GB": "GBP", "DE": "EUR", "IN": "INR", "CA": "CAD",
    "AU": "AUD", "FR": "EUR", "JP": "JPY", "BR": "BRL", "SG": "SGD",
}

EMPLOYMENT_TYPES = ["full-time", "part-time", "contract"]


# ── Helpers ────────────────────────────────────────────────────────

def load_names(filename: str) -> list[str]:
    """Load names from a text file, stripping blank lines."""
    filepath = Path(__file__).resolve().parent / filename
    with open(filepath, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def build_engine():
    """Create a SQLAlchemy engine from DATABASE_URL."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./salary_management.db")
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args)


# ── Main seed logic ───────────────────────────────────────────────

def seed(count: int = 10_000, engine=None):
    """
    Seed the database with sample data.

    1. Truncate existing data (idempotent).
    2. Insert lookup records (job_titles, departments).
    3. Generate `count` employee rows in memory.
    4. Bulk insert all rows in a single transaction.
    """
    if engine is None:
        engine = build_engine()

    rng = Random(42)
    first_names = load_names("first_names.txt")
    last_names = load_names("last_names.txt")

    Session = sessionmaker(bind=engine)

    with Session() as session:
        # ── Step 1: Truncate (dependency order) ────────────────
        session.execute(delete(Employee))
        session.execute(delete(JobTitle))
        session.execute(delete(Department))
        session.commit()

        # ── Step 2: Insert lookup tables ───────────────────────
        jt_objects = [JobTitle(title=t) for t in JOB_TITLES]
        dept_objects = [Department(name=n) for n in DEPARTMENTS]
        session.add_all(jt_objects + dept_objects)
        session.commit()

        # Build id maps
        jt_map = {jt.title: jt.id for jt in jt_objects}
        dept_map = {d.name: d.id for d in dept_objects}

        # ── Step 3: Generate employee dicts in memory ──────────
        used_emails: set[str] = set()
        rows: list[dict] = []

        for i in range(count):
            first = rng.choice(first_names)
            last = rng.choice(last_names)
            full_name = f"{first} {last}"

            # Generate unique email
            base_email = f"{first.lower()}.{last.lower()}"
            email = f"{base_email}@company.com"
            suffix = 1
            while email in used_emails:
                email = f"{base_email}{suffix}@company.com"
                suffix += 1
            used_emails.add(email)

            job_title = rng.choice(JOB_TITLES)
            department = rng.choice(DEPARTMENTS)
            country = rng.choice(COUNTRIES)
            salary_min, salary_max = SALARY_RANGES[job_title]
            salary = round(rng.uniform(salary_min, salary_max), 2)
            currency = CURRENCY_BY_COUNTRY[country]
            emp_type = rng.choices(
                EMPLOYMENT_TYPES, weights=[70, 15, 15], k=1
            )[0]

            # Random hire date between 2018-01-01 and 2025-12-31
            start_date = date(2018, 1, 1)
            days_offset = rng.randint(0, 2921)  # ~8 years
            hire_date = start_date + timedelta(days=days_offset)

            is_active = rng.random() > 0.05  # 95% active

            rows.append(
                {
                    "full_name": full_name,
                    "email": email,
                    "job_title_id": jt_map[job_title],
                    "department_id": dept_map[department],
                    "country": country,
                    "salary": salary,
                    "currency": currency,
                    "employment_type": emp_type,
                    "hire_date": hire_date,
                    "is_active": is_active,
                }
            )

        # ── Step 4: Bulk insert in single transaction ──────────
        session.execute(insert(Employee), rows)
        session.commit()

    return len(rows)


# ── CLI entrypoint ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Seed the salary management database with sample data."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10_000,
        help="Number of employee records to generate (default: 10000)",
    )
    args = parser.parse_args()

    start = time.perf_counter()
    n = seed(count=args.count)
    elapsed = time.perf_counter() - start

    print(f"Seeded {n} rows in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
