import logging
from typing import Optional, Tuple
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
    def __init__(self, session: AsyncSession, bot: Optional[Bot] = None):
        self.session = session
        self.bot = bot
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
        telegram_username: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Registration]]:
        """
        Handles the full student registration lifecycle:
        1. Validates club existence and fetches snapshot data.
        2. Upserts student record.
        3. Checks if student is already registered (Anti-duplicate rule 11).
        4. Saves new registration.
        5. Triggers admin notification via Telegram.
        """
        club_details = await self.club_repo.get_detailed_by_id(club_id)
        if not club_details:
            return False, "Tanlangan to'garak topilmadi yoki o'chirilgan.", None

        # 1. Upsert Student
        student = await self.student_repo.upsert_student(
            telegram_id=telegram_id,
            full_name=full_name.strip(),
            phone_number=phone_number.strip(),
            username=telegram_username
        )

        # 2. Check if already registered for this club
        already_registered = await self.registration_repo.is_already_registered(
            student_id=student.id,
            club_id=club_id
        )
        if already_registered:
            return False, "Siz allaqachon ushbu to'garakka ro'yxatdan o'tgansiz!", None

        # 3. Create registration with snapshot names
        registration = await self.registration_repo.create(
            student_id=student.id,
            club_id=club_id,
            course_level=course_level,
            faculty_name_snap=club_details["faculty_name"],
            direction_name_snap=club_details["direction_name"],
            status="active"
        )

        # 4. Notify administrators & management channel via Telegram bot
        if self.bot:
            try:
                from src.repositories.settings_repo import SettingsRepository
                settings_repo = SettingsRepository(self.session)
                channel_id = await settings_repo.get_admin_channel_id()
                admin_chat_ids = await self.admin_repo.get_all_notification_chat_ids()

                await NotificationService.notify_admins(
                    bot=self.bot,
                    full_name=student.full_name,
                    phone_number=student.phone_number,
                    telegram_username=student.username,
                    faculty_name=club_details["faculty_name"],
                    direction_name=club_details["direction_name"],
                    club_name=club_details["name"],
                    course_level=course_level,
                    channel_id=channel_id,
                    additional_chat_ids=admin_chat_ids
                )
            except Exception as e:
                logger.error(f"Failed to dispatch admin notification: {e}")

        return True, "Muvaffaqiyatli ro'yxatdan o'tdingiz!", registration
