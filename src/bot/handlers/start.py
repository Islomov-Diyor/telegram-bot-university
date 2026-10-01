import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.repositories.faculty_repo import FacultyRepository
from src.repositories.registration_repo import RegistrationRepository
from src.services.registration_service import RegistrationService
from src.bot.keyboards.inline_user import get_faculties_keyboard, get_leave_confirm_keyboard
from src.bot.keyboards.reply_user import get_main_menu_keyboard, remove_reply_keyboard
from src.models.student import Student
from src.models.registration import Registration
from src.models.club import Club

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
    """Display active enrollments and waiting queue entries for the student."""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Registration, Club)
            .join(Student, Registration.student_id == Student.id)
            .join(Club, Registration.club_id == Club.id)
            .where(
                (Student.telegram_id == message.from_user.id) &
                (Registration.status.in_(["active", "waiting"]))
            )
            .order_by(Registration.status.asc(), Registration.registered_at.desc())
        )
        res = await session.execute(stmt)
        rows = res.all()

    if not rows:
        await message.answer(
            "📋 <b>Siz hozircha hech qaysi to'garakka a'zo emassiz va navbatda yo'qsiz.</b>\n\n"
            "To'garaklar bilan tanishish va a'zo bo'lish uchun pastdagi "
            "<b>'🏛 To'garaklar katalogi'</b> tugmasini bosing.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    active_rows = [(r, c) for r, c in rows if r.status == "active"]
    waiting_rows = [(r, c) for r, c in rows if r.status == "waiting"]

    # 1. Send Active Clubs
    if active_rows:
        await message.answer(f"✅ <b>Siz asosiy a'zo bo'lgan to'garaklar ({len(active_rows)} ta):</b>")
        for idx, (reg, club) in enumerate(active_rows, 1):
            reg_time = reg.registered_at.strftime("%d.%m.%Y") if hasattr(reg.registered_at, "strftime") else ""
            card = (
                f"<b>{idx}. 🎯 {club.name}</b>\n"
                f"   🏛 Fakultet: {reg.faculty_name_snap}\n"
                f"   📚 Yo'nalish: {reg.direction_name_snap}\n"
                f"   🗓 Kunlar: {club.schedule_days}\n"
                f"   ⏰ Vaqt: {club.schedule_time}\n"
                f"   📍 Xona: {club.room_location}\n"
                f"   👨‍🏫 Rahbar: {club.leader_name} ({club.leader_contact})\n"
                f"   ⏱ A'zo bo'lingan: {reg_time}\n"
            )
            builder = InlineKeyboardBuilder()
            builder.button(text="❌ To'garakdan chiqish", callback_data=f"ask_leave:{reg.id}")
            await message.answer(card, reply_markup=builder.as_markup())

    # 2. Send Waiting List Clubs
    if waiting_rows:
        await message.answer(f"⏳ <b>Siz zaxira navbatida turgan to'garaklar ({len(waiting_rows)} ta):</b>")
        for idx, (reg, club) in enumerate(waiting_rows, 1):
            reg_time = reg.registered_at.strftime("%d.%m.%Y") if hasattr(reg.registered_at, "strftime") else ""
            pos = reg.queue_position or 1
            card = (
                f"<b>{idx}. 🎯 {club.name}</b>\n"
                f"   🔢 <b>Sizning navbat raqamingiz: #{pos}</b>\n"
                f"   🏛 Fakultet: {reg.faculty_name_snap}\n"
                f"   📚 Yo'nalish: {reg.direction_name_snap}\n"
                f"   🗓 Mashg'ulot kunlari: {club.schedule_days} ({club.schedule_time})\n"
                f"   ⏱ Navbatga yozilgan: {reg_time}\n\n"
                "ℹ️ <i>To'garakda bo'sh o'rin paydo bo'lishi bilan tizim sizni avtomatik asosiy a'zolikka qabul qiladi!</i>"
            )
            builder = InlineKeyboardBuilder()
            builder.button(text="❌ Navbatdan chiqish", callback_data=f"ask_leave:{reg.id}")
            await message.answer(card, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("ask_leave:"))
async def callback_ask_leave(callback: CallbackQuery):
    """Prompt student for confirmation before leaving club/queue."""
    reg_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        reg_repo = RegistrationRepository(session)
        reg = await reg_repo.get_by_id(reg_id)
        if not reg:
            await callback.answer("A'zolik yozuvi topilmadi.", show_alert=True)
            return
        
        club_stmt = select(Club).where(Club.id == reg.club_id)
        club = (await session.execute(club_stmt)).scalar_one_or_none()
        club_name = club.name if club else "To'garak"

    status_name = "asosiy a'zoligidan" if reg.status == "active" else "zaxira navbatidan"
    text = (
        f"⚠️ <b>Haqiqatdan ham '{club_name}' to'garagining {status_name} chiqmoqchimisiz?</b>\n\n"
        "<i>Agar chiqsangiz, bo'shagan o'rin navbatdagi talabaga avtomatik tarzda beriladi.</i>"
    )

    await callback.message.edit_text(text=text, reply_markup=get_leave_confirm_keyboard(reg_id))
    await callback.answer()


@router.callback_query(F.data == "cancel_leave")
async def callback_cancel_leave(callback: CallbackQuery):
    """Cancel leaving operation."""
    await callback.message.edit_text("✅ Amaliyot bekor qilindi. A'zoligingiz saqlab qolindi.")
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_leave:"))
async def callback_confirm_leave(callback: CallbackQuery, bot: Bot):
    """
    Finalize student self-withdrawal:
    Promotes next waiting student and notifies both parties!
    """
    reg_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        reg_service = RegistrationService(session=session, bot=bot)
        success, msg, promoted_info = await reg_service.cancel_registration(reg_id)

    if success:
        await callback.message.edit_text("✅ Siz to'garakdan (navbatdan) muvaffaqiyatli chiqdingiz.")
        await callback.answer("To'garakdan chiqdingiz.", show_alert=False)
    else:
        await callback.message.edit_text(f"⚠️ {msg}")
        await callback.answer(msg, show_alert=True)


@router.message(F.text == "ℹ️ Bot haqida")
async def cmd_about(message: Message):
    """Show information about the university gifted students circle system."""
    about_text = (
        "ℹ️ <b>Universitet Iqtidorli Talabalar Tizimi</b>\n\n"
        "Bu platforma universitetimizdagi iqtidorli talabalarning ilmiy, ijodiy va amaliy "
        "salohiyatini rivojlantirishga mo'ljallangan.\n\n"
        "📌 <b>Bot imkoniyatlari:</b>\n"
        "• Fakultet va yo'nalishlar kesimida to'garaklarni qidirish\n"
        "• To'garaklar sig'imi va qabul muddatlarini ko'rish\n"
        "• Asosiy o'rinlar to'lganda avtomatik navbatga yozilish\n"
        "• Bo'shagan o'rinlarga navbatdagi talabalarning avtomatik qabul qilinishi va xabardor qilinishi\n"
        "• 'Mening to'garaklarim' bo'limi orqali shaxsiy a'zoliklarni va navbatni boshqarish\n\n"
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
