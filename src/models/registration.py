from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.models.student import Student
    from src.models.club import Club


class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    club_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_level: Mapped[int] = mapped_column(Integer, nullable=False)
    faculty_name_snap: Mapped[str] = mapped_column(String(150), nullable=False)
    direction_name_snap: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Constraints: Bitta talaba bitta to'garakka faqat 1 marta a'zo bo'la oladi
    __table_args__ = (
        UniqueConstraint("student_id", "club_id", name="uq_student_club"),
    )

    # Aloqalar
    student: Mapped["Student"] = relationship("Student", back_populates="registrations", lazy="selectin")
    club: Mapped["Club"] = relationship("Club", back_populates="registrations", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Registration(id={self.id}, student_id={self.student_id}, club_id={self.club_id})>"
