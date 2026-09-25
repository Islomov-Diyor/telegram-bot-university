import asyncio
import logging
from sqlalchemy import select
from src.core.config import settings
from src.core.database import AsyncSessionLocal, create_tables
from src.models.admin import Admin
from src.models.faculty import Faculty
from src.models.direction import Direction
from src.models.club import Club
from src.core.security import get_password_hash

logger = logging.getLogger(__name__)


async def seed_initial_data():
    """Initializes tables and seeds default admin and academic club catalog."""
    await create_tables()

    async with AsyncSessionLocal() as session:
        # 1. Seed Super Admin
        admin_username = settings.ADMIN_USERNAME or "admin"
        admin_stmt = select(Admin).where(Admin.username == admin_username)
        existing_admin = (await session.execute(admin_stmt)).scalar_one_or_none()
        if not existing_admin:
            import secrets
            admin_password = settings.ADMIN_PASSWORD or f"Univ_{secrets.token_hex(6)}!#"
            admin = Admin(
                username=admin_username,
                password_hash=get_password_hash(admin_password),
                full_name="Bosh Administrator",
                role="superadmin",
                is_active=True
            )
            session.add(admin)
            print("\n" + "=" * 60)
            print("[INFO] YANGI XAVFSIZ ADMINISTRATOR AKKAUNTI YARATILDI:")
            print(f"-> Login:  {admin_username}")
            print(f"-> Parol:  {admin_password}")
            print("=" * 60 + "\n")
        elif settings.ADMIN_PASSWORD:
            existing_admin.password_hash = get_password_hash(settings.ADMIN_PASSWORD)
            print(f"[OK] Admin paroli yangilandi: {admin_username}")

        # 2. Check if faculties already exist
        fac_stmt = select(Faculty)
        existing_faculty = (await session.execute(fac_stmt)).first()
        if not existing_faculty:
            # Seed Faculties, Directions, and Clubs
            fac_eng = Faculty(name="Ingliz filologiyasi fakulteti", code="IFF", is_active=True)
            fac_rg = Faculty(name="Roman-german filologiyasi fakulteti", code="RGFF", is_active=True)
            fac_oriental = Faculty(name="Sharq tillari fakulteti", code="STF", is_active=True)
            fac_trans = Faculty(name="Tarjimashunoslik va xalqaro aloqalar fakulteti", code="TXAF", is_active=True)

            session.add_all([fac_eng, fac_rg, fac_oriental, fac_trans])
            await session.flush()

            # Directions for English Faculty
            dir_eng1 = Direction(faculty_id=fac_eng.id, name="Ingliz tili va adabiyoti", code="60111800")
            dir_eng2 = Direction(faculty_id=fac_eng.id, name="Gid hamrohligi va tarjimonlik (ingliz)", code="60230200")

            # Directions for Roman-German Faculty
            dir_rg1 = Direction(faculty_id=fac_rg.id, name="Nemis tili filologiyasi", code="60230101")
            dir_rg2 = Direction(faculty_id=fac_rg.id, name="Fransuz tili filologiyasi", code="60230102")

            # Directions for Oriental Languages
            dir_or1 = Direction(faculty_id=fac_oriental.id, name="Koreys tili va adabiyoti", code="60230103")
            dir_or2 = Direction(faculty_id=fac_oriental.id, name="Xitoy tili va adabiyoti", code="60230104")
            dir_or3 = Direction(faculty_id=fac_oriental.id, name="Yapon tili va adabiyoti", code="60230105")

            # Directions for Translation
            dir_tr1 = Direction(faculty_id=fac_trans.id, name="Sinxron tarjima", code="60230300")

            session.add_all([dir_eng1, dir_eng2, dir_rg1, dir_rg2, dir_or1, dir_or2, dir_or3, dir_tr1])
            await session.flush()

            # Clubs
            clubs = [
                Club(
                    direction_id=dir_eng1.id,
                    name="IELTS & Academic Debate Club",
                    description="Xalqaro darajadagi akademik debatlar, notiqlik mahorati va IELTS Writing/Speaking bo'yicha mahorat darslari.",
                    schedule_days="Dushanba, Chorshanba",
                    schedule_time="14:00 - 15:30",
                    room_location="302-auditoriya (A-bino)",
                    leader_name="Dots. Xoliqov Dilshod Mirzayevich",
                    leader_contact="+998901234501 / @kholiqov_ielts",
                    max_capacity=25,
                    is_active=True
                ),
                Club(
                    direction_id=dir_eng1.id,
                    name="Creative English Writing Society",
                    description="Badiiy va ilmiy maqolalar yozish, insho tayyorlash hamda xalqaro nashrlarda e'lon qilish to'garagi.",
                    schedule_days="Seshanba, Payshanba",
                    schedule_time="15:00 - 16:30",
                    room_location="215-auditoriya (A-bino)",
                    leader_name="Karimova Munira Akramovna",
                    leader_contact="+998901234502 / @karimova_m",
                    max_capacity=20,
                    is_active=True
                ),
                Club(
                    direction_id=dir_rg1.id,
                    name="Deutscher Sprachklub 'Goethe'",
                    description="Nemis tilida erkin suhbat, C1 darajasiga tayyorgarlik va Germaniya universitetlari stipendiyalari bo'yicha tahliliy seminar.",
                    schedule_days="Seshanba, Juma",
                    schedule_time="14:30 - 16:00",
                    room_location="405-auditoriya (B-bino)",
                    leader_name="Rustamov Shuhrat Aliyevich",
                    leader_contact="+998901234503 / @rustamov_de",
                    max_capacity=20,
                    is_active=True
                ),
                Club(
                    direction_id=dir_or1.id,
                    name="Hangul Talent & Culture Circle",
                    description="Koreys tili TOPIK II tayyorgarligi, notiqlik bellashuvlari va ilmiy maqolalar tayyorlash to'garagi.",
                    schedule_days="Dushanba, Payshanba",
                    schedule_time="15:00 - 16:30",
                    room_location="110-auditoriya (Sharq binosi)",
                    leader_name="Kim Sun-Mi (Xorijiy mutaxassis)",
                    leader_contact="+998901234504 / @kimsunmi_circle",
                    max_capacity=25,
                    is_active=True
                ),
                Club(
                    direction_id=dir_tr1.id,
                    name="Bo'lajak Sinxron Tarjimonlar Laboratoriyasi",
                    description="Maxsus lingvafon xonasida professional kabina orqali sinxron va ketma-ket tarjima mahoratini oshirish laboratoriyasi.",
                    schedule_days="Chorshanba, Shanba",
                    schedule_time="11:00 - 12:30",
                    room_location="Sinxron tarjima markazi (2-zal)",
                    leader_name="Prof. Yo'ldoshev Akmal Bahodirovich",
                    leader_contact="+998901234505 / @prof_yuldoshev",
                    max_capacity=15,
                    is_active=True
                )
            ]
            session.add_all(clubs)
            print(" Initial academic clubs seeded successfully!")

        await session.commit()
        print(" Database initialized and seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_initial_data())
