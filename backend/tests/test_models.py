"""
Test models — verify ORM round-trip in an in-memory SQLite database.

Creates all tables, inserts one JobTitle + Department + Employee,
and asserts that reading them back returns the same values.
"""

from datetime import date, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models.job_title import JobTitle
from app.models.department import Department
from app.models.employee import Employee


@pytest.fixture
def db_session():
    """Create a fresh in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


class TestJobTitle:
    def test_create_and_read(self, db_session: Session):
        jt = JobTitle(title="Software Engineer")
        db_session.add(jt)
        db_session.commit()

        result = db_session.query(JobTitle).filter_by(title="Software Engineer").first()
        assert result is not None
        assert result.id is not None
        assert result.title == "Software Engineer"

    def test_unique_constraint(self, db_session: Session):
        db_session.add(JobTitle(title="Designer"))
        db_session.commit()

        db_session.add(JobTitle(title="Designer"))
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestDepartment:
    def test_create_and_read(self, db_session: Session):
        dept = Department(name="Engineering")
        db_session.add(dept)
        db_session.commit()

        result = db_session.query(Department).filter_by(name="Engineering").first()
        assert result is not None
        assert result.id is not None
        assert result.name == "Engineering"

    def test_unique_constraint(self, db_session: Session):
        db_session.add(Department(name="HR"))
        db_session.commit()

        db_session.add(Department(name="HR"))
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestEmployee:
    def test_create_and_read_with_relationships(self, db_session: Session):
        """Insert one JobTitle + Department + Employee, verify round-trip."""
        # Create lookup records
        jt = JobTitle(title="Data Scientist")
        dept = Department(name="Analytics")
        db_session.add_all([jt, dept])
        db_session.commit()

        # Create employee
        emp = Employee(
            full_name="Alice Johnson",
            email="alice@example.com",
            job_title_id=jt.id,
            department_id=dept.id,
            country="US",
            salary=120000.00,
            currency="USD",
            employment_type="full-time",
            hire_date=date(2024, 3, 15),
            is_active=True,
        )
        db_session.add(emp)
        db_session.commit()

        # Read back and assert
        result = db_session.query(Employee).filter_by(email="alice@example.com").first()
        assert result is not None
        assert result.id is not None
        assert result.full_name == "Alice Johnson"
        assert result.email == "alice@example.com"
        assert result.job_title_id == jt.id
        assert result.department_id == dept.id
        assert result.country == "US"
        assert result.salary == 120000.00
        assert result.currency == "USD"
        assert result.employment_type == "full-time"
        assert result.hire_date == date(2024, 3, 15)
        assert result.is_active is True
        assert result.created_at is not None
        assert result.updated_at is not None

        # Verify relationships
        assert result.job_title.title == "Data Scientist"
        assert result.department.name == "Analytics"

    def test_unique_email_constraint(self, db_session: Session):
        """Duplicate emails should raise an IntegrityError."""
        jt = JobTitle(title="Engineer")
        dept = Department(name="Eng")
        db_session.add_all([jt, dept])
        db_session.commit()

        emp1 = Employee(
            full_name="Bob",
            email="bob@example.com",
            job_title_id=jt.id,
            department_id=dept.id,
            country="GB",
            salary=80000,
            currency="GBP",
            employment_type="full-time",
            hire_date=date(2023, 1, 10),
        )
        db_session.add(emp1)
        db_session.commit()

        emp2 = Employee(
            full_name="Bob Clone",
            email="bob@example.com",  # duplicate
            job_title_id=jt.id,
            department_id=dept.id,
            country="GB",
            salary=85000,
            currency="GBP",
            employment_type="contract",
            hire_date=date(2024, 6, 1),
        )
        db_session.add(emp2)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_indexes_exist(self, db_session: Session):
        """Verify the three custom indexes are present in the table metadata."""
        indexes = {idx.name for idx in Employee.__table__.indexes}
        assert "ix_emp_country" in indexes
        assert "ix_emp_jt_country" in indexes
        assert "ix_emp_active" in indexes

    def test_default_values(self, db_session: Session):
        """Verify default values for currency, employment_type, is_active."""
        jt = JobTitle(title="Manager")
        dept = Department(name="Operations")
        db_session.add_all([jt, dept])
        db_session.commit()

        emp = Employee(
            full_name="Carol",
            email="carol@example.com",
            job_title_id=jt.id,
            department_id=dept.id,
            country="DE",
            salary=95000,
            hire_date=date(2024, 1, 1),
        )
        db_session.add(emp)
        db_session.commit()

        result = db_session.query(Employee).filter_by(email="carol@example.com").first()
        assert result.currency == "USD"
        assert result.employment_type == "full-time"
        assert result.is_active is True
