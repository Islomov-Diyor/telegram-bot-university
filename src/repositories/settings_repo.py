from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.system_setting import SystemSetting
from src.repositories.base import BaseRepository
from src.core.config import settings


class SettingsRepository(BaseRepository[SystemSetting]):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemSetting, session)

    async def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        stmt = select(SystemSetting).where(SystemSetting.key == key)
        result = await self.session.execute(stmt)
        record = result.scalars().first()
        return record.value if record else default

    async def set_setting(self, key: str, value: str) -> SystemSetting:
        stmt = select(SystemSetting).where(SystemSetting.key == key)
        result = await self.session.execute(stmt)
        record = result.scalars().first()
        if record:
            record.value = value.strip()
            await self.session.commit()
            await self.session.refresh(record)
            return record
        else:
            return await self.create(key=key, value=value.strip())

    async def get_admin_channel_id(self) -> Optional[str]:
        """Fetch the management channel ID, falling back to .env ADMIN_CHANNEL_ID."""
        db_val = await self.get_setting("admin_channel_id")
        if db_val and db_val.strip():
            return db_val.strip()
        return settings.ADMIN_CHANNEL_ID

    async def set_admin_channel_id(self, channel_id: str) -> SystemSetting:
        """Store management channel ID or @username in the database."""
        return await self.set_setting("admin_channel_id", channel_id.strip())
