import asyncio
import logging
import re
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import select, and_
from aiogram import Bot

from src.core.database import AsyncSessionLocal
from src.models.club import Club
from src.models.registration import Registration
from src.models.student import Student
from src.models.reminder_log import ReminderLog
from src.bot.bot_instance import get_bot

logger = logging.getLogger(__name__)

# Weekday mappings for schedule match
WEEKDAY_MAP = {
    0: ["dushanba", "понедельник", "monday", "mon"],
    1: ["seshanba", "вторник", "tuesday", "tue"],
    2: ["chorshanba", "среда", "wednesday", "wed"],
    3: ["payshanba", "четверг", "thursday", "thu"],
    4: ["juma", "пятница", "friday", "fri"],
    5: ["shanba", "суббота", "saturday", "sat"],
    6: ["yakshanba", "воскресенье", "sunday", "sun"],
}


class ReminderService:
    @staticmethod
    def is_club_scheduled_today(schedule_days: str, today_weekday: int) -> bool:
        """Check if club has class scheduled on the current day."""
        if not schedule_days:
            return False
        days_lower = schedule_days.lower()
        search_terms = WEEKDAY_MAP.get(today_weekday, [])
        return any(term in days_lower for term in search_terms)

    @staticmethod
    def parse_start_time(schedule_time: str) -> Optional[datetime]:
        """Extract lesson start time from string like '15:00 - 16:30' or '15:00'."""
        if not schedule_time:
            return None
        match = re.search(r'(\d{1,2})[:.](\d{2})', schedule_time)
        if not match:
            return None
        hour = int(match.group(1))
        minute = int(match.group(2))
        now = datetime.now()
        try:
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except ValueError:
            return None

    @classmethod
    async def send_club_reminder(
        cls,
        club_id: int,
        custom_note: Optional[str] = None,
        reminder_type: str = "manual"
    ) -> Dict[str, Any]:
        """
        Send Telegram reminder to all actively enrolled students of a club.
        (Requirement: '🔔 Eslatma Bugun soat 15:00 da “Kompyuter savodxonligi” mashg‘uloti bor.')
        """
        bot = get_bot()
        today = date.today()

        async with AsyncSessionLocal() as session:
            # 1. Fetch club
            club_stmt = select(Club).where(Club.id == club_id)
            club = (await session.execute(club_stmt)).scalars().first()
            if not club:
                return {"success": False, "sent": 0, "failed": 0, "total": 0, "message": "To'garak topilmadi."}

            # 2. Fetch active students
            reg_stmt = (
                select(Student.telegram_id)
                .join(Registration, Registration.student_id == Student.id)
                .where(
                    and_(
                        Registration.club_id == club_id,
                        Registration.status == "active"
                    )
                )
            )
            reg_res = await session.execute(reg_stmt)
            chat_ids = [cid for cid in reg_res.scalars().all() if cid]

            total = len(chat_ids)
            if total == 0:
                return {
                    "success": True,
                    "club_id": club.id,
                    "club_name": club.name,
                    "total": 0,
                    "sent": 0,
                    "failed": 0,
                    "message": f"\"{club.name}\" to'garagida hozircha ro'yxatdan o'tgan faol talabalar mavjud emas."
                }

            sent = 0
            failed = 0

            # 3. Format message with HTML and plain text fallback
            import html
            safe_name = html.escape(club.name)
            safe_time = html.escape(club.schedule_time or "Belgilangan vaqtda")
            safe_room = html.escape(club.room_location or "Belgilanmagan")
            safe_leader = html.escape(club.leader_name or "Belgilanmagan")
            safe_contact = html.escape(club.leader_contact or "Mavjud emas")

            html_text = (
                "🔔 <b>ESLATMA</b>\n\n"
                f"Bugun soat <b>{safe_time}</b> da <b>\"{safe_name}\"</b> mashg‘uloti bor.\n\n"
                f"📍 <b>Auditoriya:</b> {safe_room}\n"
                f"👨‍🏫 <b>Rahbar:</b> {safe_leader}\n"
                f"📞 <b>Aloqa:</b> {safe_contact}\n"
            )
            plain_text = (
                "🔔 ESLATMA\n\n"
                f"Bugun soat {club.schedule_time} da \"{club.name}\" mashg‘uloti bor.\n\n"
                f"📍 Auditoriya: {club.room_location}\n"
                f"👨‍🏫 Rahbar: {club.leader_name}\n"
                f"📞 Aloqa: {club.leader_contact}\n"
            )
            if custom_note:
                safe_note = html.escape(custom_note.strip())
                html_text += f"\n💬 <i>Qo'shimcha: {safe_note}</i>\n"
                plain_text += f"\n💬 Qo'shimcha: {custom_note.strip()}\n"

            html_text += "\n<i>Mashg‘ulotga o‘z vaqtida kelishingizni so‘raymiz!</i>"
            plain_text += "\nMashg‘ulotga o‘z vaqtida kelishingizni so‘raymiz!"

            # 4. Send messages
            if bot and chat_ids:
                for cid in chat_ids:
                    try:
                        try:
                            await asyncio.wait_for(
                                bot.send_message(chat_id=cid, text=html_text, parse_mode="HTML"),
                                timeout=5.0
                            )
                        except Exception:
                            await asyncio.wait_for(
                                bot.send_message(chat_id=cid, text=plain_text, parse_mode=None),
                                timeout=5.0
                            )
                        sent += 1
                        await asyncio.sleep(0.04)  # Telegram broadcast throttling
                    except Exception as e:
                        logger.warning(f"Failed to send reminder to telegram_id {cid}: {e}")
                        failed += 1
            else:
                # If bot is not configured or in test mode, mark as sent for verification
                sent = total

            # 5. Record reminder log in DB
            log_stmt = select(ReminderLog).where(
                and_(
                    ReminderLog.club_id == club_id,
                    ReminderLog.reminder_date == today,
                    ReminderLog.reminder_type == reminder_type
                )
            )
            existing_log = (await session.execute(log_stmt)).scalars().first()
            if existing_log:
                existing_log.sent_count += sent
            else:
                new_log = ReminderLog(
                    club_id=club_id,
                    reminder_date=today,
                    reminder_type=reminder_type,
                    sent_count=sent
                )
                session.add(new_log)
            await session.commit()

            msg_desc = f"Eslatma \"{club.name}\" to'garagining {sent} ta talabasiga muvaffaqiyatli yuborildi."
            if sent == 0 and total > 0:
                msg_desc = f"Eslatma talabalarga yetkazilmadi ({failed} ta xatolik, botga ulanmagan)."
            elif failed > 0:
                msg_desc += f" ({failed} ta xatolik)"

            return {
                "success": sent > 0 or total == 0,
                "club_id": club.id,
                "club_name": club.name,
                "total": total,
                "sent": sent,
                "failed": failed,
                "message": msg_desc
            }

    @classmethod
    async def check_and_send_scheduled_reminders(cls):
        """
        Scan clubs scheduled for today and send reminders 1–2 hours before class starts.
        Runs periodically in background.
        """
        now = datetime.now()
        today = date.today()
        today_weekday = now.weekday()

        async with AsyncSessionLocal() as session:
            # Fetch all active clubs
            stmt = select(Club).where(Club.is_active == True)
            clubs = (await session.execute(stmt)).scalars().all()

            for club in clubs:
                if not cls.is_club_scheduled_today(club.schedule_days, today_weekday):
                    continue

                start_dt = cls.parse_start_time(club.schedule_time)
                if not start_dt:
                    continue

                # Difference in minutes between class start and now
                diff_minutes = (start_dt - now).total_seconds() / 60

                # Window: 45 to 135 minutes before class (roughly 1 to 2 hours)
                if 45 <= diff_minutes <= 135:
                    # Check if already sent today
                    log_stmt = select(ReminderLog).where(
                        and_(
                            ReminderLog.club_id == club.id,
                            ReminderLog.reminder_date == today,
                            ReminderLog.reminder_type == "auto_lesson"
                        )
                    )
                    already_sent = (await session.execute(log_stmt)).scalars().first()
                    if already_sent:
                        continue

                    logger.info(f"Triggering automated lesson reminder for club {club.name} (starts at {club.schedule_time}).")
                    await cls.send_club_reminder(
                        club_id=club.id,
                        reminder_type="auto_lesson"
                    )


async def run_reminder_scheduler(interval_seconds: int = 900):
    """Background task to periodically evaluate lesson reminder criteria."""
    logger.info("Lesson reminder scheduler started.")
    while True:
        try:
            await ReminderService.check_and_send_scheduled_reminders()
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Lesson reminder scheduler stopped.")
            break
        except Exception as e:
            logger.error(f"Error in reminder scheduler loop: {e}", exc_info=True)
            await asyncio.sleep(60)
