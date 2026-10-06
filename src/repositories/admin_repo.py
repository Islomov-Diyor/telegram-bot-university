from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.admin import Admin
from src.repositories.base import BaseRepository
from src.core.security import get_password_hash


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, session: AsyncSession):
        super().__init__(Admin, session)

    async def get_by_username(self, username: str) -> Optional[Admin]:
        stmt = select(Admin).where(Admin.username == username.strip())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_admin(
        self,
        username: str,
        plain_password: str,
        full_name: str,
        role: str = "superadmin",
        telegram_chat_id: Optional[int] = None
    ) -> Admin:
        password_hash = get_password_hash(plain_password)
        return await self.create(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            telegram_chat_id=telegram_chat_id,
            is_active=True
        )

    async def get_all_notification_chat_ids(self) -> List[int]:
        """Fetch all active admin telegram chat IDs who should receive notifications."""
        stmt = (
            select(Admin.telegram_chat_id)
            .where(
                (Admin.is_active == True) &
                (Admin.telegram_chat_id != None)
            )
        )
        result = await self.session.execute(stmt)
        return [chat_id for chat_id in result.scalars().all() if chat_id]

    async def get_all_teachers(self) -> List[Admin]:
        """Fetch all teacher accounts with assigned clubs."""
        stmt = select(Admin).where(Admin.role == "teacher").order_by(Admin.id.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_teacher(
        self,
        username: str,
        plain_password: str,
        full_name: str,
        club_id: Optional[int] = None
    ) -> Admin:
        """Create a new teacher user account assigned to a specific club."""
        password_hash = get_password_hash(plain_password)
        return await self.create(
            username=username.strip(),
            password_hash=password_hash,
            full_name=full_name.strip(),
            role="teacher",
            club_id=club_id,
            is_active=True
        )

    async def update_teacher(
        self,
        teacher_id: int,
        full_name: Optional[str] = None,
        club_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        plain_password: Optional[str] = None
    ) -> Optional[Admin]:
        """Update teacher account details or reset password."""
        teacher = await self.get_by_id(teacher_id)
        if not teacher or teacher.role != "teacher":
            return None

        if full_name is not None:
            teacher.full_name = full_name.strip()
        if club_id is not None:
            teacher.club_id = club_id
        if is_active is not None:
            teacher.is_active = is_active
        if plain_password:
            teacher.password_hash = get_password_hash(plain_password)

        await self.session.commit()
        await self.session.refresh(teacher)
        return teacher

