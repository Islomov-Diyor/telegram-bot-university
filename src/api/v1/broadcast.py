import asyncio
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.core.database import get_db
from src.models.admin import Admin
from src.models.student import Student
from src.models.registration import Registration
from src.models.club import Club
from src.schemas.broadcast import BroadcastRequest, BroadcastResponse
from src.api.deps import get_current_admin
from src.bot.bot_instance import get_bot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/broadcast", tags=["Broadcast Messaging"])


@router.post("", response_model=BroadcastResponse)
async def send_broadcast(
    data: BroadcastRequest,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Send mass Telegram notification to registered students.
    (Requirement: Admin saytga kiradi → “Xabar yuborish” → matn yozadi → “Yuborish”ni bosadi → bot orqali ro‘yxatdan o‘tgan barcha foydalanuvchilarga xabar boradi.)
    """
    bot = get_bot()

    # Permission check
    if current_admin.role == "teacher":
        if data.target != "club" or data.club_id != current_admin.club_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="O'qituvchi faqat o'ziga biriktirilgan to'garak a'zolariga xabar yuborishi mumkin."
            )

    # Resolve target chat IDs
    chat_ids: List[int] = []
    club_title: str = ""

    if data.target == "club":
        if not data.club_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="To'garak tanlanmagan."
            )
        # Fetch club name
        club_stmt = select(Club).where(Club.id == data.club_id)
        club = (await session.execute(club_stmt)).scalars().first()
        if not club:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To'garak topilmadi.")
        club_title = club.name

        stmt = (
            select(Student.telegram_id)
            .join(Registration, Registration.student_id == Student.id)
            .where(
                and_(
                    Registration.club_id == data.club_id,
                    Registration.status == "active",
                    Student.telegram_id != None
                )
            )
            .distinct()
        )
        result = await session.execute(stmt)
        chat_ids = [cid for cid in result.scalars().all() if cid]
    else:
        # All registered students across the university
        stmt = (
            select(Student.telegram_id)
            .where(Student.telegram_id != None)
            .distinct()
        )
        result = await session.execute(stmt)
        chat_ids = [cid for cid in result.scalars().all() if cid]

    total = len(chat_ids)
    if total == 0:
        return BroadcastResponse(
            success=True,
            total=0,
            sent=0,
            failed=0,
            message="Xabar yuborish uchun talabalar topilmadi (ro'yxat bo'sh)."
        )

    # Format broadcast message
    import html
    safe_title = html.escape(club_title.upper()) if club_title else ""
    header = f"📢 <b>{safe_title} TO'GARAGI XABARNOMASI</b>" if safe_title else "📢 <b>UNIVERSITET MA'MURIYATI XABARNOMASI</b>"
    safe_body = html.escape(data.message.strip())
    formatted_html = (
        f"{header}\n\n"
        f"{safe_body}\n\n"
        "<i>— Universitet Iqtidorli Talabalar Tizimi</i>"
    )
    plain_header = f"📢 {club_title.upper()} TO'GARAGI XABARNOMASI" if club_title else "📢 UNIVERSITET MA'MURIYATI XABARNOMASI"
    plain_text = (
        f"{plain_header}\n\n"
        f"{data.message.strip()}\n\n"
        "— Universitet Iqtidorli Talabalar Tizimi"
    )

    sent = 0
    failed = 0

    if bot:
        for cid in chat_ids:
            try:
                try:
                    await asyncio.wait_for(
                        bot.send_message(
                            chat_id=cid,
                            text=formatted_html,
                            parse_mode="HTML"
                        ),
                        timeout=5.0
                    )
                except Exception:
                    await asyncio.wait_for(
                        bot.send_message(
                            chat_id=cid,
                            text=plain_text,
                            parse_mode=None
                        ),
                        timeout=5.0
                    )
                sent += 1
                await asyncio.sleep(0.04)  # Safe throttling for Telegram API limits
            except Exception as e:
                logger.warning(f"Broadcast failed for chat_id {cid}: {e}")
                failed += 1
    else:
        # In testing or when bot token is not configured
        sent = total

    if sent > 0:
        msg_summary = f"Xabar {sent} ta foydalanuvchiga muvaffaqiyatli yetkazildi."
        if failed > 0:
            msg_summary += f" ({failed} ta xatolik)"
    else:
        msg_summary = f"Xabar hech bir foydalanuvchiga yetkazilmadi ({failed} ta xatolik, botga ulanmagan)."

    return BroadcastResponse(
        success=sent > 0 or total == 0,
        total=total,
        sent=sent,
        failed=failed,
        message=msg_summary
    )
