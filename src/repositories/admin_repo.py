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
