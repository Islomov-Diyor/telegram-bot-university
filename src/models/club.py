from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.models.direction import Direction
    from src.models.registration import Registration


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    direction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("directions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    schedule_days: Mapped[str] = mapped_column(String(100), nullable=False)  # Masalan: "Seshanba, Payshanba"
    schedule_time: Mapped[str] = mapped_column(String(50), nullable=False)   # Masalan: "15:00 - 17:00"
    room_location: Mapped[str] = mapped_column(String(100), nullable=False)  # Masalan: "B-bino, 304-auditoriya"
    leader_name: Mapped[str] = mapped_column(String(150), nullable=False)    # Masalan: "Dots. Eshmatov T.M."
    leader_contact: Mapped[str] = mapped_column(String(100), nullable=False) # Masalan: "+998901234567 / @eshmatov"
    max_capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Aloqalar
    direction: Mapped["Direction"] = relationship("Direction", back_populates="clubs", lazy="selectin")
    registrations: Mapped[List["Registration"]] = relationship(
        "Registration", back_populates="club", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Club(id={self.id}, name='{self.name}', leader='{self.leader_name}')>"
