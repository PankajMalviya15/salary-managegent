"""Department model — normalised lookup table for departments."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Relationship back to employees
    employees: Mapped[list["Employee"]] = relationship(  # noqa: F821
        "Employee", back_populates="department"
    )

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name='{self.name}')>"
