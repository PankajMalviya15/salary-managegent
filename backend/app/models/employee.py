"""
Employee model — central entity storing employee compensation data.

Includes three custom indexes for common query patterns:
  - ix_emp_country       → filter/group by country
  - ix_emp_jt_country    → analytics joining job_title + country
  - ix_emp_active        → filter active/inactive employees
"""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        Index("ix_emp_country", "country"),
        Index("ix_emp_jt_country", "job_title_id", "country"),
        Index("ix_emp_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Foreign keys to lookup tables
    job_title_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("job_titles.id"), nullable=False
    )
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=False
    )

    country: Mapped[str] = mapped_column(String(2), nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    employment_type: Mapped[str] = mapped_column(
        String, nullable=False, default="full-time"
    )
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    job_title: Mapped["JobTitle"] = relationship(  # noqa: F821
        "JobTitle", back_populates="employees"
    )
    department: Mapped["Department"] = relationship(  # noqa: F821
        "Department", back_populates="employees"
    )

    def __repr__(self) -> str:
        return (
            f"<Employee(id={self.id}, name='{self.full_name}', "
            f"email='{self.email}', country='{self.country}', "
            f"salary={self.salary})>"
        )
