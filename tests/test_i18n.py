import pytest
import time
from unittest.mock import AsyncMock, MagicMock
from src.core.database import AsyncSessionLocal, create_tables
from src.models.faculty import Faculty
from src.models.direction import Direction
from src.models.club import Club
from src.models.student import Student
from src.models.registration import Registration
from src.repositories.student_repo import StudentRepository
from src.repositories.club_repo import ClubRepository
from src.repositories.direction_repo import DirectionRepository
from src.repositories.faculty_repo import FacultyRepository
from src.services.registration_service import RegistrationService
from src.bot.i18n import get_text, LANGUAGES


def test_i18n_get_text():
    assert "Assalomu alaykum" in get_text("welcome_title", "uz")
    assert "Здравствуйте" in get_text("welcome_title", "ru")
    assert "Welcome" in get_text("welcome_title", "en")

    # Fallback to uz for unknown language
    assert "Assalomu alaykum" in get_text("welcome_title", "fr")

    # Format parameter substitution
    msg_uz = get_text("lang_changed", "uz", lang_name="O'zbekcha")
    assert "O'zbekcha" in msg_uz
    msg_ru = get_text("lang_changed", "ru", lang_name="Русский")
    assert "Русский" in msg_ru
    msg_en = get_text("lang_changed", "en", lang_name="English")
    assert "English" in msg_en


@pytest.mark.asyncio
async def test_student_language_persistence():
    await create_tables()
    suffix = int(time.time_ns() % 1000000)

    async with AsyncSessionLocal() as session:
        student_repo = StudentRepository(session)

        # Set language for new student
        tg_id = 900000 + suffix
        student = await student_repo.set_language(
            telegram_id=tg_id,
            language="ru",
            username="rustudent"
        )
        assert student.language == "ru"
        assert student.telegram_id == tg_id

        # Query language
        lang = await student_repo.get_language(tg_id)
        assert lang == "ru"

        # Switch language to English
        student = await student_repo.set_language(
            telegram_id=tg_id,
            language="en"
        )
        assert student.language == "en"

        lang2 = await student_repo.get_language(tg_id)
        assert lang2 == "en"


@pytest.mark.asyncio
async def test_promotion_notification_in_student_language():
    await create_tables()
    suffix = int(time.time_ns() % 1000000)
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()

    async with AsyncSessionLocal() as session:
        fac_repo = FacultyRepository(session)
        faculties = await fac_repo.get_all()
        fac = faculties[0]

        dir_repo = DirectionRepository(session)
        dirs = await dir_repo.get_active_by_faculty(fac.id)
        direction = dirs[0]

        club_repo = ClubRepository(session)
        club = await club_repo.create(
            direction_id=direction.id,
            name=f"Lang Club {suffix}",
            description="Multi-language test",
            schedule_days="Mon, Wed",
            schedule_time="15:00",
            room_location="Room 101",
            leader_name="Mr. Smith",
            leader_contact="+998901234567",
            max_capacity=1,
            is_active=True
        )

        service = RegistrationService(session=session, bot=mock_bot)

        # 2. Register Student 1 (Active spot) in Uzbek
        tg1 = 100000 + suffix
        ok1, _, reg1 = await service.register_student(
            telegram_id=tg1,
            full_name="Talaba Bir",
            phone_number="+998901111111",
            club_id=club.id,
            course_level=2,
            language="uz"
        )
        assert ok1 is True
        assert reg1.status == "active"

        # 3. Register Student 2 (Waiting queue #1) in Russian
        tg2 = 200000 + suffix
        ok2, _, reg2 = await service.register_student(
            telegram_id=tg2,
            full_name="Студент Два",
            phone_number="+998902222222",
            club_id=club.id,
            course_level=3,
            language="ru"
        )
        assert ok2 is True
        assert reg2.status == "waiting"

        # 4. Student 1 cancels/leaves club
        mock_bot.send_message.reset_mock()
        ok_cancel, _, promo_info = await service.cancel_registration(reg1.id)
        assert ok_cancel is True
        assert promo_info is not None
        assert promo_info["telegram_id"] == tg2

        # 5. Check promotion notification was sent in Russian to Student 2
        mock_bot.send_message.assert_called_once()
        args, kwargs = mock_bot.send_message.call_args
        assert kwargs["chat_id"] == tg2
        assert "ОТЛИЧНАЯ НОВОСТЬ!" in kwargs["text"]
        assert "Студент Два" in kwargs["text"]
        assert club.name in kwargs["text"]
