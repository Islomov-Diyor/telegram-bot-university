import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.core.database import AsyncSessionLocal, create_tables
from src.core.seed import seed_initial_data
from src.core.config import settings
from src.repositories.club_repo import ClubRepository
from src.repositories.registration_repo import RegistrationRepository
from src.services.registration_service import RegistrationService
from src.services.export_service import ExportService


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_database_initialization_and_seed():
    """Verify tables exist and seed data populated faculties and clubs."""
    await seed_initial_data()

    async with AsyncSessionLocal() as session:
        club_repo = ClubRepository(session)
        clubs = await club_repo.get_all()
        assert len(clubs) > 0, "Initial clubs should be seeded into database"
        assert clubs[0].name != "", "Club name should be populated"


@pytest.mark.asyncio
async def test_student_registration_and_duplicate_prevention():
    """
    Verify student registration lifecycle and requirement 11:
    'Bir foydalanuvchi aynan bir to'garakka bir necha marta ro'yxatdan o'ta olmasligi kerak.'
    """
    async with AsyncSessionLocal() as session:
        club_repo = ClubRepository(session)
        clubs = await club_repo.get_all()
        assert len(clubs) > 0
        test_club = clubs[0]

        reg_service = RegistrationService(session=session, bot=None)

        import time
        unique_tg_id = int(time.time_ns() % 10000000000)

        # 1. First registration should succeed
        success, msg, reg = await reg_service.register_student(
            telegram_id=unique_tg_id,
            full_name="Nodirbek Rustamov",
            phone_number="+998901112233",
            club_id=test_club.id,
            course_level=2,
            telegram_username="nodir_dev"
        )
        assert success is True
        assert reg is not None
        assert "Muvaffaqiyatli" in msg

        # 2. Second registration to the SAME club MUST be rejected (Requirement 11)
        dup_success, dup_msg, dup_reg = await reg_service.register_student(
            telegram_id=unique_tg_id,
            full_name="Nodirbek Rustamov",
            phone_number="+998901112233",
            club_id=test_club.id,
            course_level=2,
            telegram_username="nodir_dev"
        )
        assert dup_success is False, "Duplicate registration MUST be rejected"
        assert dup_reg is None
        assert "allaqachon" in dup_msg.lower()


@pytest.mark.asyncio
async def test_excel_and_csv_export():
    """Verify requirement 15: Excel and CSV export generation."""
    async with AsyncSessionLocal() as session:
        reg_repo = RegistrationRepository(session)
        items = await reg_repo.get_all_for_export()
        assert len(items) > 0, "Should have registrations from previous test"

        # Excel (.xlsx) check
        excel_buf = ExportService.generate_excel(items)
        assert excel_buf is not None
        excel_bytes = excel_buf.getvalue()
        assert len(excel_bytes) > 1000, "Excel file should have substantial binary content"
        # PK is the zip signature of modern xlsx
        assert excel_bytes.startswith(b"PK"), "Excel file must start with PK zip header"

        # CSV (.csv) check
        csv_buf = ExportService.generate_csv(items)
        assert csv_buf is not None
        csv_bytes = csv_buf.getvalue()
        assert len(csv_bytes) > 50
        # Check UTF-8 BOM
        assert csv_bytes.startswith(b"\xef\xbb\xbf"), "CSV file must include UTF-8 BOM for Excel compatibility"


@pytest.mark.asyncio
async def test_rest_api_auth_and_endpoints():
    """Verify REST API authentication, statistics, clubs, and export endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Invalid login
        bad_login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword"})
        assert bad_login.status_code == 401

        # 2. Valid login
        curr_pwd = settings.ADMIN_PASSWORD
        login_res = await client.post("/api/v1/auth/login", json={"username": "admin", "password": curr_pwd})
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. /auth/me
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["username"] == "admin"

        # 4. /stats/overview
        stats_res = await client.get("/api/v1/stats/overview", headers=headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["clubs_count"] > 0
        assert stats["students_count"] > 0

        # 4.1 /auth/change-password tests
        # Bad current password
        bad_change = await client.put(
            "/api/v1/auth/change-password",
            json={"current_password": "wrongpassword", "new_password": "NewStrongPass2026!"},
            headers=headers
        )
        assert bad_change.status_code == 400

        # Too short password (caught by Pydantic min_length=8)
        short_change = await client.put(
            "/api/v1/auth/change-password",
            json={"current_password": curr_pwd, "new_password": "short"},
            headers=headers
        )
        assert short_change.status_code == 422

        # Successful change
        temp_pwd = "SuperSecurePass2026!#"
        good_change = await client.put(
            "/api/v1/auth/change-password",
            json={"current_password": curr_pwd, "new_password": temp_pwd},
            headers=headers
        )
        assert good_change.status_code == 200

        # Verify old password no longer works
        old_login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": curr_pwd})
        assert old_login.status_code == 401

        # Verify new password works
        new_login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": temp_pwd})
        assert new_login.status_code == 200

        # Restore original password for clean state
        headers = {"Authorization": f"Bearer {new_login.json()['access_token']}"}
        restore_change = await client.put(
            "/api/v1/auth/change-password",
            json={"current_password": temp_pwd, "new_password": curr_pwd},
            headers=headers
        )
        assert restore_change.status_code == 200

        # 5. /clubs
        clubs_res = await client.get("/api/v1/clubs", headers=headers)
        assert clubs_res.status_code == 200
        clubs = clubs_res.json()
        assert len(clubs) > 0
        # Check fields required by requirement 13 & 14
        first_club = clubs[0]
        assert "schedule_days" in first_club
        assert "schedule_time" in first_club
        assert "room_location" in first_club
        assert "leader_name" in first_club
        assert "leader_contact" in first_club
        assert "students_count" in first_club

        # 6. /registrations
        reg_res = await client.get("/api/v1/registrations", headers=headers)
        assert reg_res.status_code == 200
        reg_data = reg_res.json()
        assert "items" in reg_data
        assert reg_data["total"] > 0

        # 7. /export/excel
        excel_res = await client.get("/api/v1/export/excel", headers=headers)
        assert excel_res.status_code == 200
        assert "application/vnd.openxmlformats" in excel_res.headers.get("content-type", "")

        # 8. /export/csv
        csv_res = await client.get("/api/v1/export/csv", headers=headers)
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers.get("content-type", "")

        # 9. /settings/channel (Get & Put)
        put_chan = await client.put(
            "/api/v1/settings/channel",
            json={"channel_id": "@universitet_iqtidorli_test"},
            headers=headers
        )
        assert put_chan.status_code == 200

        get_chan = await client.get("/api/v1/settings/channel", headers=headers)
        assert get_chan.status_code == 200
        assert get_chan.json()["channel_id"] == "@universitet_iqtidorli_test"


@pytest.mark.asyncio
async def test_student_can_join_multiple_different_clubs():
    """
    Verify requirement:
    'bir nechta tugarakga azo bulishi mumkin'
    A student CAN successfully join multiple DIFFERENT clubs.
    """
    import time
    async with AsyncSessionLocal() as session:
        club_repo = ClubRepository(session)
        clubs = await club_repo.get_all()
        assert len(clubs) >= 2, "Need at least 2 clubs to test multiple club membership"

        club_1 = clubs[0]
        club_2 = clubs[1]

        unique_tg_id = int(time.time_ns() % 10000000000)
        reg_service = RegistrationService(session=session, bot=None)

        # 1. Register for Club 1
        res1, msg1, reg1 = await reg_service.register_student(
            telegram_id=unique_tg_id,
            full_name="Dilshod Karimov",
            phone_number="+998909876543",
            club_id=club_1.id,
            course_level=3,
            telegram_username="dilshod_k"
        )
        assert res1 is True
        assert reg1 is not None

        # 2. Register for Club 2 (Different club) - MUST SUCCEED!
        res2, msg2, reg2 = await reg_service.register_student(
            telegram_id=unique_tg_id,
            full_name="Dilshod Karimov",
            phone_number="+998909876543",
            club_id=club_2.id,
            course_level=3,
            telegram_username="dilshod_k"
        )
        assert res2 is True, "Student must be able to join multiple different clubs"
        assert reg2 is not None
        assert reg2.club_id != reg1.club_id

