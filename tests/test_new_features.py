import pytest
import asyncio
from datetime import date
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.core.database import AsyncSessionLocal
from src.core.config import settings
from src.repositories.club_repo import ClubRepository
from src.services.reminder_service import ReminderService


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_teacher_role_creation_and_permissions():
    """
    Verify Requirement 2:
    - Admin creates teacher account with login and password
    - Teacher logs into system
    - Teacher only has access to scoped functions, forbidden from admin actions
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as Superadmin
        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD}
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Get clubs
        clubs_res = await client.get("/api/v1/clubs", headers=admin_headers)
        assert clubs_res.status_code == 200
        clubs = clubs_res.json()
        assert len(clubs) > 0
        assigned_club = clubs[0]

        # 2. Superadmin creates a new teacher
        teacher_username = f"ustoz_{assigned_club['id']}"
        create_teacher_res = await client.post(
            "/api/v1/teachers",
            json={
                "username": teacher_username,
                "password": "TeacherPass2026!#",
                "full_name": "Aziz Olimov",
                "club_id": assigned_club["id"]
            },
            headers=admin_headers
        )
        # 201 Created or 400 if already exists
        if create_teacher_res.status_code == 400:
            pass # already created from previous run
        else:
            assert create_teacher_res.status_code == 201
            data = create_teacher_res.json()
            assert data["username"] == teacher_username
            assert data["role"] == "teacher"
            assert data["club_id"] == assigned_club["id"]

        # 3. Teacher logs in
        teacher_login = await client.post(
            "/api/v1/auth/login",
            json={"username": teacher_username, "password": "TeacherPass2026!#"}
        )
        assert teacher_login.status_code == 200
        teacher_token = teacher_login.json()["access_token"]
        teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

        # 4. Teacher checks /auth/me
        me_res = await client.get("/api/v1/auth/me", headers=teacher_headers)
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["role"] == "teacher"
        assert me_data["club_id"] == assigned_club["id"]

        # 4b. Teacher accesses /clubs -> returns only their assigned club
        teacher_clubs_res = await client.get("/api/v1/clubs", headers=teacher_headers)
        assert teacher_clubs_res.status_code == 200
        t_clubs = teacher_clubs_res.json()
        assert len(t_clubs) == 1
        assert t_clubs[0]["id"] == assigned_club["id"]

        # 5. Teacher FORBIDDEN actions:
        # - Cannot list faculties (403)
        bad_fac_list = await client.get("/api/v1/faculties", headers=teacher_headers)
        assert bad_fac_list.status_code == 403

        # - Cannot list directions (403)
        bad_dir_list = await client.get("/api/v1/directions", headers=teacher_headers)
        assert bad_dir_list.status_code == 403

        # - Cannot view admin dashboard overview stats (403)
        bad_stats = await client.get("/api/v1/stats/overview", headers=teacher_headers)
        assert bad_stats.status_code == 403

        # - Cannot create faculty
        bad_fac = await client.post(
            "/api/v1/faculties",
            json={"name": "Forbidden Faculty"},
            headers=teacher_headers
        )
        assert bad_fac.status_code == 403

        # - Cannot delete club
        bad_club_del = await client.delete(
            f"/api/v1/clubs/{assigned_club['id']}",
            headers=teacher_headers
        )
        assert bad_club_del.status_code == 403

        # - Cannot manage settings
        bad_settings = await client.get("/api/v1/settings/channel", headers=teacher_headers)
        assert bad_settings.status_code == 403

        # - Cannot create another teacher
        bad_create_t = await client.post(
            "/api/v1/teachers",
            json={"username": "fake", "password": "123", "full_name": "Fake"},
            headers=teacher_headers
        )
        assert bad_create_t.status_code == 403


@pytest.mark.asyncio
async def test_broadcast_messaging():
    """
    Verify Requirement 1:
    - Admin navigates to 'Xabar yuborish', enters text, sends message
    - Registered users receive message via Telegram bot
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Superadmin login
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD}
        )
        admin_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        # Send mass message to all
        broadcast_res = await client.post(
            "/api/v1/broadcast",
            json={
                "message": "Hurmatli talabalar! Ertaga universitetda iqtidorli yoshlar festivali bo'lib o'tadi.",
                "target": "all"
            },
            headers=admin_headers
        )
        assert broadcast_res.status_code == 200
        data = broadcast_res.json()
        assert data["success"] is True
        assert "message" in data


@pytest.mark.asyncio
async def test_attendance_and_results():
    """
    Verify Requirement 4:
    - Teacher takes attendance for each lesson (har darsda davomat qiladi)
    - System calculates total lessons attended and percentage (nechta darsga qatnashgani, qatnashish foizi)
    - Excel report download
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Superadmin login
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD}
        )
        admin_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        # Get clubs
        clubs_res = await client.get("/api/v1/clubs", headers=admin_headers)
        club = clubs_res.json()[0]
        club_id = club["id"]

        # 1. Create a lesson session
        today_str = date.today().isoformat()
        lesson_res = await client.post(
            "/api/v1/attendance/lessons",
            json={
                "club_id": club_id,
                "lesson_date": today_str,
                "topic": "1-Mavzu: Kirish va Tanishtiruv"
            },
            headers=admin_headers
        )
        assert lesson_res.status_code == 201
        lesson = lesson_res.json()
        lesson_id = lesson["id"]

        # 2. Fetch lesson roster
        roster_res = await client.get(
            f"/api/v1/attendance/lessons/{lesson_id}",
            headers=admin_headers
        )
        assert roster_res.status_code == 200
        roster = roster_res.json()
        assert "students" in roster
        students = roster["students"]

        # 3. Mark attendance if students exist
        if students:
            first_student = students[0]
            save_res = await client.post(
                f"/api/v1/attendance/lessons/{lesson_id}/save",
                json={
                    "records": [
                        {
                            "student_id": first_student["student_id"],
                            "status": "present",
                            "notes": "Faol qatnashdi"
                        }
                    ]
                },
                headers=admin_headers
            )
            assert save_res.status_code == 200

        # 4. Fetch Course Attendance Results (Natijalar)
        results_res = await client.get(
            f"/api/v1/attendance/results?club_id={club_id}",
            headers=admin_headers
        )
        assert results_res.status_code == 200
        results = results_res.json()
        assert results["total_lessons_held"] >= 1
        assert "students_summary" in results

        if results["students_summary"]:
            s_sum = results["students_summary"][0]
            assert "attended_lessons" in s_sum
            assert "attendance_percentage" in s_sum
            assert "grade_label" in s_sum
            assert 0.0 <= s_sum["attendance_percentage"] <= 100.0

        # 5. Export attendance Excel
        excel_res = await client.get(
            f"/api/v1/attendance/export?club_id={club_id}",
            headers=admin_headers
        )
        assert excel_res.status_code == 200
        assert "application/vnd.openxmlformats" in excel_res.headers.get("content-type", "")
        assert len(excel_res.content) > 1000


@pytest.mark.asyncio
async def test_lesson_reminders():
    """
    Verify Requirement 3:
    - Reminder formatting and trigger for upcoming lessons
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Superadmin login
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": settings.ADMIN_PASSWORD}
        )
        admin_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        # Get clubs
        clubs_res = await client.get("/api/v1/clubs", headers=admin_headers)
        club = clubs_res.json()[0]

        # Trigger manual reminder endpoint
        remind_res = await client.post(
            f"/api/v1/clubs/{club['id']}/remind",
            json={"custom_note": "Iltimos, daftaringizni unutmang."},
            headers=admin_headers
        )
        assert remind_res.status_code == 200
        data = remind_res.json()
        assert data["success"] is True
        assert data["club_id"] == club["id"]

    # Verify schedule matching helper
    assert ReminderService.is_club_scheduled_today("Dushanba, Chorshanba", 0) is True
    assert ReminderService.is_club_scheduled_today("Seshanba, Payshanba", 0) is False
    assert ReminderService.parse_start_time("15:00 - 17:00") is not None
