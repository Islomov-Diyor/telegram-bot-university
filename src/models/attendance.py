from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.models.club import Club
    from src.models.student import Student
    from src.models.admin import Admin


class AttendanceLesson(Base):
    __tablename__ = "attendance_lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    club_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    topic: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Aloqalar
    club: Mapped["Club"] = relationship("Club", lazy="selectin")
    created_by: Mapped[Optional["Admin"]] = relationship("Admin", lazy="selectin")
    records: Mapped[List["AttendanceRecord"]] = relationship(
        "AttendanceRecord", back_populates="lesson", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AttendanceLesson(id={self.id}, club_id={self.club_id}, date={self.lesson_date})>"


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attendance_lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="present", nullable=False)  # present, absent, excused
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Constraints: Bitta darsda bitta talaba uchun faqat bitta belgilash
    __table_args__ = (
        UniqueConstraint("lesson_id", "student_id", name="uq_lesson_student"),
    )

    # Aloqalar
    lesson: Mapped["AttendanceLesson"] = relationship("AttendanceLesson", back_populates="records", lazy="selectin")
    student: Mapped["Student"] = relationship("Student", lazy="selectin")

    def __repr__(self) -> str:
        return f"<AttendanceRecord(lesson_id={self.lesson_id}, student_id={self.student_id}, status={self.status})>"
