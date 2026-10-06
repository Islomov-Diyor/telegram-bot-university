from datetime import datetime, date
from typing import TYPE_CHECKING
from sqlalchemy import Integer, Date, DateTime, String, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.models.club import Club


class ReminderLog(Base):
    __tablename__ = "reminder_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    club_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reminder_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    reminder_type: Mapped[str] = mapped_column(
        String(50), default="auto_lesson", nullable=False
    )  # auto_lesson, manual
    sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("club_id", "reminder_date", "reminder_type", name="uq_club_date_type"),
    )

    club: Mapped["Club"] = relationship("Club", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ReminderLog(club_id={self.club_id}, date={self.reminder_date}, sent={self.sent_count})>"
