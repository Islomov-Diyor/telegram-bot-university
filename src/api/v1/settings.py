from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.settings_repo import SettingsRepository
from src.services.notification_service import NotificationService
from src.bot.bot_instance import get_bot
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/settings", tags=["System Settings"])


class ChannelUpdateRequest(BaseModel):
    channel_id: str = Field(..., min_length=2, description="Telegram kanal ID (-100...) yoki @username")


@router.get("/channel")
async def get_channel_setting(
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Retrieve the configured management Telegram channel ID or username."""
    repo = SettingsRepository(session)
    channel_id = await repo.get_admin_channel_id()
    return {"channel_id": channel_id or ""}


@router.put("/channel")
async def update_channel_setting(
    data: ChannelUpdateRequest,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Update the management Telegram channel ID or username."""
    repo = SettingsRepository(session)
    await repo.set_admin_channel_id(data.channel_id)
    return {"message": "Boshqaruv kanali muvaffaqiyatli saqlandi.", "channel_id": data.channel_id}


@router.post("/test-channel")
async def test_channel_notification(
    data: ChannelUpdateRequest,
    current_admin: Admin = Depends(get_current_admin)
):
    """Send a test message to the configured channel to verify bot write permissions."""
    bot = get_bot()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BOT_TOKEN konfiguratsiya qilinmagan. Avval .env faylida bot tokenini ko'rsating."
        )

    success = await NotificationService.send_test_notification(bot, data.channel_id.strip())
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Kanalga xabar yuborib bo'lmadi! "
                "Iltimos, botni ushbu kanalga qo'shganingizni va unga 'Admin' "
                "(Xabar yozish ruxsati) berganingizni tekshiring."
            )
        )

    return {"message": "Sinov xabari kanalga muvaffaqiyatli yuborildi!"}
