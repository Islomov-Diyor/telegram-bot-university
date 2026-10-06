from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, BigInteger, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.models.club import Club


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="superadmin", nullable=False) # superadmin, teacher
    club_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    telegram_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    club: Mapped[Optional["Club"]] = relationship("Club", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Admin(id={self.id}, username='{self.username}', role='{self.role}')>"

