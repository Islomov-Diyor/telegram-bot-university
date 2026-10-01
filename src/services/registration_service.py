import logging
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot

from src.models.registration import Registration
from src.repositories.student_repo import StudentRepository
from src.repositories.club_repo import ClubRepository
from src.repositories.registration_repo import RegistrationRepository
from src.repositories.admin_repo import AdminRepository
from src.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class RegistrationService:
    def __init__(self, session: AsyncSession, bot: Optional[Any] = None):
        self.session = session
        if bot is False:
            self.bot = None
        elif bot is not None:
            self.bot = bot
        else:
            try:
                from src.bot.bot_instance import get_bot
                self.bot = get_bot()
            except Exception:
                self.bot = None

        self.student_repo = StudentRepository(session)
        self.club_repo = ClubRepository(session)
        self.registration_repo = RegistrationRepository(session)
        self.admin_repo = AdminRepository(session)

    async def register_student(
        self,
        telegram_id: int,
        full_name: str,
        phone_number: str,
        club_id: int,
        course_level: int,
        telegram_username: Optional[str] = None,
        language: Optional[str] = "uz"
    ) -> Tuple[bool, str, Optional[Registration]]:
        """
        Handles the full student registration lifecycle:
        1. Validates club existence and checks registration deadline.
        2. Upserts student record with language.
        3. Prevents duplicate enrollment (active or waiting).
        4. Checks max capacity:
           - If active spots available -> enrolls as 'active'.
           - If full -> enrolls on 'waiting' list with queue number.
        5. Triggers admin notification via Telegram.
        """
        club_details = await self.club_repo.get_detailed_by_id(club_id)
        if not club_details:
            return False, "Tanlangan to'garak topilmadi yoki o'chirilgan.", None

        # 1. Check Registration Deadline (Belgilangan muddat tugasa -> yopiladi)
        deadline = club_details.get("registration_deadline")
        if deadline:
            now_utc = datetime.now(timezone.utc)
            deadline_utc = deadline if deadline.tzinfo else deadline.replace(tzinfo=timezone.utc)
            if now_utc > deadline_utc:
                deadline_str = deadline.strftime("%d.%m.%Y %H:%M")
                return (
                    False,
                    f"Ushbu to'garakka ro'yxatdan o'tish muddati ({deadline_str}) tugagan. "
                    "Yangi arizalar va navbatga yozilish yopilgan.",
                    None
                )

        # 2. Upsert Student
        student = await self.student_repo.upsert_student(
            telegram_id=telegram_id,
            full_name=full_name.strip(),
            phone_number=phone_number.strip(),
            username=telegram_username,
            language=language or "uz"
        )

        # 3. Check if student already has a record for this club
        existing_reg = await self.registration_repo.get_by_student_and_club(
            student_id=student.id,
            club_id=club_id
        )
        if existing_reg:
            if existing_reg.status == "active":
                return False, "Siz allaqachon ushbu to'garakka asosiy a'zo bo'lgansiz!", None
            elif existing_reg.status == "waiting":
                pos = f" (#{existing_reg.queue_position})" if existing_reg.queue_position else ""
                return False, f"Siz allaqachon ushbu to'garak zaxira navbatidasiz{pos}!", None
            else:
                # Delete former cancelled registration so new one can be created
                await self.registration_repo.delete(existing_reg.id)

        # 4. Check Club Capacity (Max capacity & Waiting queue)
        max_capacity = club_details.get("max_capacity") or 0
        active_count = await self.registration_repo.count_active_by_club(club_id)

        if max_capacity > 0 and active_count >= max_capacity:
            # Main spots are full! Put student on waiting list
            waiting_count = await self.registration_repo.count_waiting_by_club(club_id)
            new_queue_pos = waiting_count + 1

            registration = await self.registration_repo.create(
                student_id=student.id,
                club_id=club_id,
                course_level=course_level,
                faculty_name_snap=club_details["faculty_name"],
                direction_name_snap=club_details["direction_name"],
                status="waiting",
                queue_position=new_queue_pos
            )

            msg = (
                f"To'garakda asosiy o'rinlar to'lgan ({active_count}/{max_capacity}). "
                f"Siz zaxiraga (navbatga) #{new_queue_pos} bo'lib yozildingiz."
            )
        else:
            # Active registration
            registration = await self.registration_repo.create(
                student_id=student.id,
                club_id=club_id,
                course_level=course_level,
                faculty_name_snap=club_details["faculty_name"],
                direction_name_snap=club_details["direction_name"],
                status="active",
                queue_position=None
            )
            msg = "Muvaffaqiyatli ro'yxatdan o'tdingiz!"

        # 5. Notify administrators via Telegram bot
        if self.bot:
            try:
                from src.repositories.settings_repo import SettingsRepository
                settings_repo = SettingsRepository(self.session)
                channel_id = await settings_repo.get_admin_channel_id()
                admin_chat_ids = await self.admin_repo.get_all_notification_chat_ids()

                status_label = "✅ ASOSIY A'ZO" if registration.status == "active" else f"⏳ NAVBATDA (#{registration.queue_position})"
                await NotificationService.notify_admins(
                    bot=self.bot,
                    full_name=student.full_name,
                    phone_number=student.phone_number,
                    telegram_username=student.username,
                    faculty_name=club_details["faculty_name"],
                    direction_name=club_details["direction_name"],
                    club_name=f"{club_details['name']} [{status_label}]",
                    course_level=course_level,
                    channel_id=channel_id,
                    additional_chat_ids=admin_chat_ids
                )
            except Exception as e:
                logger.error(f"Failed to dispatch admin notification: {e}")

        return True, msg, registration

    async def cancel_registration(
        self,
        registration_id: int
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Cancels / deletes a registration and automatically promotes the next
        queued student from the waiting list:
        'Kimdir chiqib ketsa -> navbatdagi odamga avtomatik xabar beriladi.'
        """
        registration = await self.registration_repo.get_by_id(registration_id)
        if not registration:
            return False, "A'zolik yozuvi topilmadi.", None

        club_id = registration.club_id
        was_active = (registration.status == "active")

        # Delete the registration record
        await self.registration_repo.delete(registration_id)

        promoted_info = None

        if was_active:
            # A spot in the club opened up! Check waiting list
            next_waiting = await self.registration_repo.get_next_waiting_student(club_id)
            if next_waiting:
                # Promote to active!
                next_waiting.status = "active"
                next_waiting.queue_position = None
                await self.session.commit()
                await self.session.refresh(next_waiting)

                # Re-order the rest of the queue
                await self.registration_repo.reorder_queue(club_id)

                # Fetch promoted student and club details
                promoted_student = await self.student_repo.get_by_id(next_waiting.student_id)
                club = await self.club_repo.get_by_id(club_id)

                if promoted_student and club:
                    promoted_info = {
                        "student_id": promoted_student.id,
                        "full_name": promoted_student.full_name,
                        "telegram_id": promoted_student.telegram_id,
                        "club_name": club.name
                    }

                    # Send immediate automatic Telegram notification in student's language
                    if self.bot:
                        try:
                            from src.bot.i18n import get_text
                            student_lang = getattr(promoted_student, "language", "uz") or "uz"
                            promo_text = get_text(
                                "promotion_notification",
                                student_lang,
                                full_name=promoted_student.full_name or "Talaba",
                                club_name=club.name,
                                faculty_name=next_waiting.faculty_name_snap,
                                direction_name=next_waiting.direction_name_snap,
                                schedule_days=club.schedule_days,
                                schedule_time=club.schedule_time,
                                room_location=club.room_location,
                                leader_name=club.leader_name,
                                leader_contact=club.leader_contact
                            )
                            await self.bot.send_message(
                                chat_id=promoted_student.telegram_id,
                                text=promo_text,
                                parse_mode="HTML"
                            )
                            logger.info(f"Notified promoted student {promoted_student.full_name} ({promoted_student.telegram_id}) for club {club.name} in [{student_lang}]")
                        except Exception as e:
                            logger.error(f"Failed to send Telegram notification to promoted student: {e}")
                            logger.error(f"Failed to send Telegram notification to promoted student: {e}")
        else:
            # A waiting student left the queue: re-order remaining waiting queue
            await self.registration_repo.reorder_queue(club_id)

        msg = "A'zolik muvaffaqiyatli bekor qilindi."
        if promoted_info:
            msg += f" Navbatdagi talaba ({promoted_info['full_name']}) avtomatik qabul qilindi va bot orqali xabar yuborildi!"

        return True, msg, promoted_info
