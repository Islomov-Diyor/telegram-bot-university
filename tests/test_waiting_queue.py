import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from src.core.database import AsyncSessionLocal, create_tables
from src.repositories.club_repo import ClubRepository
from src.repositories.student_repo import StudentRepository
from src.repositories.registration_repo import RegistrationRepository
from src.repositories.direction_repo import DirectionRepository
from src.repositories.faculty_repo import FacultyRepository
from src.services.registration_service import RegistrationService
from src.models.club import Club
from src.models.registration import Registration


@pytest.mark.asyncio
async def test_capacity_waiting_queue_and_promotion():
    """
    Test complete lifecycle of:
    1. Max capacity reached -> next student placed in waiting list (queue)
    2. Promotion: when active student leaves, next in queue is promoted to active
    3. Reordering of remaining queue
    4. Deadline expiration blocks registration
    """
    await create_tables()

    async with AsyncSessionLocal() as session:
        fac_repo = FacultyRepository(session)
        faculties = await fac_repo.get_all()
        assert len(faculties) > 0
        fac = faculties[0]

        dir_repo = DirectionRepository(session)
        dirs = await dir_repo.get_active_by_faculty(fac.id)
        assert len(dirs) > 0
        direction = dirs[0]

        club_repo = ClubRepository(session)
        # Create a test club with max_capacity = 2
        import time
        suffix = int(time.time_ns() % 1000000)
        test_club = await club_repo.create(
            direction_id=direction.id,
            name=f"Queue Test Club {suffix}",
            description="Testing capacity limits and waiting queue",
            schedule_days="Dushanba, Juma",
            schedule_time="16:00 - 17:30",
            room_location="101-xona",
            leader_name="Test O'qituvchi",
            leader_contact="+998901112233",
            max_capacity=2,
            is_active=True
        )

        reg_service = RegistrationService(session=session, bot=False)
        reg_repo = RegistrationRepository(session)

        # 1. Register Student 1 (Spot 1/2) -> active
        s1_id = 900000000 + suffix
        ok1, msg1, reg1 = await reg_service.register_student(
            telegram_id=s1_id,
            full_name="Talaba Birinchi",
            phone_number="+998901111111",
            club_id=test_club.id,
            course_level=1
        )
        assert ok1 is True
        assert reg1.status == "active"
        assert reg1.queue_position is None

        # 2. Register Student 2 (Spot 2/2) -> active
        s2_id = 900000001 + suffix
        ok2, msg2, reg2 = await reg_service.register_student(
            telegram_id=s2_id,
            full_name="Talaba Ikkinchi",
            phone_number="+998901111112",
            club_id=test_club.id,
            course_level=2
        )
        assert ok2 is True
        assert reg2.status == "active"
        assert reg2.queue_position is None

        # 3. Register Student 3 (Club is now FULL: 2/2) -> waiting #1
        s3_id = 900000002 + suffix
        ok3, msg3, reg3 = await reg_service.register_student(
            telegram_id=s3_id,
            full_name="Talaba Uchinchi (Zaxira)",
            phone_number="+998901111113",
            club_id=test_club.id,
            course_level=3
        )
        assert ok3 is True
        assert reg3.status == "waiting"
        assert reg3.queue_position == 1

        # 4. Register Student 4 (Club is still FULL) -> waiting #2
        s4_id = 900000003 + suffix
        ok4, msg4, reg4 = await reg_service.register_student(
            telegram_id=s4_id,
            full_name="Talaba To'rtinchi (Zaxira)",
            phone_number="+998901111114",
            club_id=test_club.id,
            course_level=4
        )
        assert ok4 is True
        assert reg4.status == "waiting"
        assert reg4.queue_position == 2

        # 5. Check duplicate rejection for waiting student
        dup_ok, dup_msg, _ = await reg_service.register_student(
            telegram_id=s3_id,
            full_name="Talaba Uchinchi",
            phone_number="+998901111113",
            club_id=test_club.id,
            course_level=3
        )
        assert dup_ok is False
        assert "navbatdasiz" in dup_msg.lower() or "zaxira" in dup_msg.lower()

        # 6. Verify stats for this club
        detailed = await club_repo.get_detailed_by_id(test_club.id)
        assert detailed["students_count"] == 2
        assert detailed["active_students_count"] == 2
        assert detailed["waiting_students_count"] == 2
        assert detailed["is_full"] is True

        # 7. PROMOTION TEST: Student 1 leaves / gets cancelled!
        cancel_ok, cancel_msg, promoted_info = await reg_service.cancel_registration(reg1.id)
        assert cancel_ok is True
        assert promoted_info is not None
        assert promoted_info["full_name"] == "Talaba Uchinchi"

        # Verify Student 3 is now ACTIVE!
        await session.refresh(reg3)
        assert reg3.status == "active"
        assert reg3.queue_position is None

        # Verify Student 4 was re-ordered to queue position 1!
        await session.refresh(reg4)
        assert reg4.status == "waiting"
        assert reg4.queue_position == 1

        # 8. DEADLINE TEST: Set deadline in the past
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        await club_repo.update(test_club.id, registration_deadline=past_time)

        # Try to register a new student 5
        s5_id = 900000004 + suffix
        ok5, msg5, reg5 = await reg_service.register_student(
            telegram_id=s5_id,
            full_name="Talaba Beshinchi",
            phone_number="+998901111115",
            club_id=test_club.id,
            course_level=1
        )
        assert ok5 is False
        assert "muddati" in msg5.lower() and "tugagan" in msg5.lower()

        # Clean up test club
        await club_repo.delete(test_club.id)
