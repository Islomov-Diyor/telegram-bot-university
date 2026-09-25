import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.core.database import AsyncSessionLocal
from src.repositories.faculty_repo import FacultyRepository
from src.bot.keyboards.inline_user import get_faculties_keyboard
from src.bot.keyboards.reply_user import get_main_menu_keyboard, remove_reply_keyboard

logger = logging.getLogger(__name__)
router = Router(name="start_router")


@router.message(CommandStart())
@router.message(F.text == "🏛 To'garaklar katalogi")
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command and catalog requests."""
    await state.clear()

    async with AsyncSessionLocal() as session:
        faculty_repo = FacultyRepository(session)
        faculties = await faculty_repo.get_active_faculties()

    if not faculties:
        await message.answer(
            "Assalomu alaykum!\n\n"
            "Hozirda tizimda faol fakultetlar yoki to'garaklar mavjud emas. "
            "Iltimos, keyinroq qayta tekshiring.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    text = (
        "👋 <b>Assalomu alaykum, hurmatli talaba!</b>\n\n"
        "🏛 <b>UNIVERSITET IQTIDORLI TALABALAR BOTI</b>ga xush kelibsiz!\n\n"
        "Ushbu bot orqali universitetimizdagi barcha ilmiy, ijodiy va fan to'garaklari "
        "haqida to'liq ma'lumot olishingiz hamda o'zingiz qiziqqan to'garakka online a'zo bo'lishingiz mumkin.\n\n"
        "⬇️ <i>Boshlash uchun quyidagi ro'yxatdan o'zingiz tahsil olayotgan fakultetni tanlang:</i>"
    )

    await message.answer(
        text=text,
        reply_markup=get_faculties_keyboard(faculties)
    )


@router.message(Command("my_clubs"))
@router.message(F.text == "📋 Mening to'garaklarim")
async def cmd_my_clubs(message: Message):
    """Display all active clubs the student is currently enrolled in."""
    from sqlalchemy import select
    from src.models.student import Student
    from src.models.registration import Registration
    from src.models.club import Club

    async with AsyncSessionLocal() as session:
        # Find student by telegram_id
        stmt = (
            select(Registration, Club)
            .join(Student, Registration.student_id == Student.id)
            .join(Club, Registration.club_id == Club.id)
            .where(
                (Student.telegram_id == message.from_user.id) &
                (Registration.status == "active")
            )
            .order_by(Registration.registered_at.desc())
        )
        res = await session.execute(stmt)
        rows = res.all()

    if not rows:
        await message.answer(
            "📋 <b>Siz hozircha hech qaysi to'garakka a'zo emassiz.</b>\n\n"
            "To'garaklar bilan tanishish va a'zo bo'lish uchun pastdagi "
            "<b>'🏛 To'garaklar katalogi'</b> tugmasini bosing.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    text_parts = [
        f"📋 <b>Siz a'zo bo'lgan to'garaklar ro'yxati ({len(rows)} ta):</b>\n"
    ]

    for idx, (reg, club) in enumerate(rows, 1):
        reg_time = reg.registered_at.strftime("%d.%m.%Y") if hasattr(reg.registered_at, "strftime") else ""
        text_parts.append(
            f"<b>{idx}. 🎯 {club.name}</b>\n"
            f"   🏛 Fakultet: {reg.faculty_name_snap}\n"
            f"   📚 Yo'nalish: {reg.direction_name_snap}\n"
            f"   🗓 Mashg'ulot kunlari: {club.schedule_days}\n"
            f"   ⏰ Vaqti: {club.schedule_time}\n"
            f"   📍 Xonasi: {club.room_location}\n"
            f"   👨‍🏫 Rahbar: {club.leader_name} ({club.leader_contact})\n"
            f"   ⏱ A'zo bo'lingan sana: {reg_time}\n"
        )

    text_parts.append("<i>Yana boshqa to'garaklarga a'zo bo'lish uchun katalogdan foydalanishingiz mumkin.</i>")

    await message.answer("\n".join(text_parts), reply_markup=get_main_menu_keyboard())


@router.message(F.text == "ℹ️ Bot haqida")
async def cmd_about(message: Message):
    """Show information about the university gifted students circle system."""
    about_text = (
        "ℹ️ <b>Universitet Iqtidorli Talabalar Tizimi</b>\n\n"
        "Bu platforma universitetimizdagi iqtidorli talabalarning ilmiy, ijodiy va amaliy "
        "salohiyatini rivojlantirishga mo'ljallangan.\n\n"
        "📌 <b>Bot imkoniyatlari:</b>\n"
        "• Fakultet va yo'nalishlar kesimida to'garaklarni qidirish\n"
        "• Mashg'ulotlar vaqti, joyi va rahbari bilan tanishish\n"
        "• Bir necha xil to'garaklarga erkin a'zo bo'lish\n"
        "• 'Mening to'garaklarim' bo'limi orqali a'zo bo'lgan to'garaklar jadvalini kuzatish\n\n"
        "To'garaklar katalogiga o'tish uchun quyidagi tugmani bosing."
    )
    await message.answer(about_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current active FSM operation."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Hech qanday faol jarayon yo'q.", reply_markup=get_main_menu_keyboard())
        return

    await state.clear()
    await message.answer(
        "❌ Amaliyot bekor qilindi. Bosh sahifaga qaytish uchun /start ni bosing.",
        reply_markup=get_main_menu_keyboard()
    )
