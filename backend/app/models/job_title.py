"""JobTitle model — normalised lookup table for job titles."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobTitle(Base):
    __tablename__ = "job_titles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Relationship back to employees
    employees: Mapped[list["Employee"]] = relationship(  # noqa: F821
        "Employee", back_populates="job_title"
    )

    def __repr__(self) -> str:
        return f"<JobTitle(id={self.id}, title='{self.title}')>"
