import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.repositories.faculty_repo import FacultyRepository
from src.repositories.registration_repo import RegistrationRepository
from src.repositories.student_repo import StudentRepository
from src.services.registration_service import RegistrationService
from src.bot.keyboards.inline_user import get_faculties_keyboard, get_leave_confirm_keyboard
from src.bot.keyboards.reply_user import get_main_menu_keyboard
from src.bot.i18n import get_text, get_user_lang, get_lang_inline_keyboard, LANGUAGES
from src.models.student import Student
from src.models.registration import Registration
from src.models.club import Club

logger = logging.getLogger(__name__)
router = Router(name="start_router")

CATALOG_BUTTONS = ["🏛 To'garaklar katalogi", "🏛 Каталог кружков", "🏛 Clubs catalog"]
MY_CLUBS_BUTTONS = ["📋 Mening to'garaklarim", "📋 Мои кружки", "📋 My clubs"]
ABOUT_BUTTONS = ["ℹ️ Bot haqida", "ℹ️ О боте", "ℹ️ About bot"]
LANG_BUTTONS = ["🌐 Til / Language", "🌐 Язык / Language", "🌐 Language / Til", "🌐 Til", "🌐 Язык", "🌐 Language"]
CANCEL_BUTTONS = ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]


@router.message(Command("language"))
@router.message(Command("til"))
@router.message(F.text.in_(LANG_BUTTONS))
async def cmd_language(message: Message):
    """Prompt user to choose communication language."""
    await message.answer(
        text=get_text("choose_language", "uz"),
        reply_markup=get_lang_inline_keyboard()
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def callback_set_language(callback: CallbackQuery, state: FSMContext):
    """Save selected language to database and FSM state, then present main menu."""
    lang = callback.data.split(":")[1]
    if lang not in LANGUAGES:
        lang = "uz"

    # Persist in DB and FSM
    await state.update_data(user_lang=lang)

    async with AsyncSessionLocal() as session:
        student_repo = StudentRepository(session)
        await student_repo.set_language(
            telegram_id=callback.from_user.id,
            language=lang,
            username=callback.from_user.username
        )

        faculty_repo = FacultyRepository(session)
        faculties = await faculty_repo.get_active_faculties()

    lang_name = LANGUAGES.get(lang, "O'zbekcha")
    await callback.message.delete()

    # Send confirmation & updated bottom keyboard
    await callback.message.answer(
        text=get_text("lang_changed", lang, lang_name=lang_name),
        reply_markup=get_main_menu_keyboard(lang)
    )

    # Present faculties catalog
    if not faculties:
        await callback.message.answer(get_text("no_faculties", lang))
    else:
        await callback.message.answer(
            text=get_text("welcome_title", lang),
            reply_markup=get_faculties_keyboard(faculties, lang)
        )

    await callback.answer()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    await state.clear()

    async with AsyncSessionLocal() as session:
        student_repo = StudentRepository(session)
        student = await student_repo.get_by_telegram_id(message.from_user.id)

        # If user has not chosen language yet, prompt for language
        if not student or not getattr(student, "language", None):
            await message.answer(
                text=get_text("choose_language", "uz"),
                reply_markup=get_lang_inline_keyboard()
            )
            return

        lang = student.language
        await state.update_data(user_lang=lang)

        faculty_repo = FacultyRepository(session)
        faculties = await faculty_repo.get_active_faculties()

    if not faculties:
        await message.answer(
            get_text("no_faculties", lang),
            reply_markup=get_main_menu_keyboard(lang)
        )
        return

    await message.answer(
        text=get_text("welcome_title", lang),
        reply_markup=get_faculties_keyboard(faculties, lang)
    )


@router.message(F.text.in_(CATALOG_BUTTONS))
async def cmd_catalog(message: Message, state: FSMContext):
    """Show catalog of faculties in user's preferred language."""
    await state.clear()
    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(message.from_user.id, session, state)
        faculty_repo = FacultyRepository(session)
        faculties = await faculty_repo.get_active_faculties()

    if not faculties:
        await message.answer(
            get_text("no_faculties", lang),
            reply_markup=get_main_menu_keyboard(lang)
        )
        return

    await message.answer(
        text=get_text("catalog_faculties_title", lang),
        reply_markup=get_faculties_keyboard(faculties, lang)
    )


@router.message(Command("my_clubs"))
@router.message(F.text.in_(MY_CLUBS_BUTTONS))
async def cmd_my_clubs(message: Message, state: FSMContext):
    """Display active enrollments and waiting queue entries for the student."""
    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(message.from_user.id, session, state)
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
            get_text("my_clubs_empty", lang),
            reply_markup=get_main_menu_keyboard(lang)
        )
        return

    active_rows = [(r, c) for r, c in rows if r.status == "active"]
    waiting_rows = [(r, c) for r, c in rows if r.status == "waiting"]

    # 1. Send Active Clubs
    if active_rows:
        await message.answer(get_text("my_active_title", lang, count=len(active_rows)))
        for idx, (reg, club) in enumerate(active_rows, 1):
            reg_time = reg.registered_at.strftime("%d.%m.%Y") if hasattr(reg.registered_at, "strftime") else ""
            card = (
                f"<b>{idx}. 🎯 {club.name}</b>\n"
                f"   🏛 {reg.faculty_name_snap}\n"
                f"   📚 {reg.direction_name_snap}\n"
                f"   🗓 {club.schedule_days}\n"
                f"   ⏰ {club.schedule_time}\n"
                f"   📍 {club.room_location}\n"
                f"   👨‍🏫 {club.leader_name} ({club.leader_contact})\n"
                f"   ⏱ {reg_time}\n"
            )
            builder = InlineKeyboardBuilder()
            builder.button(text=get_text("btn_leave_club", lang), callback_data=f"ask_leave:{reg.id}")
            await message.answer(card, reply_markup=builder.as_markup())

    # 2. Send Waiting List Clubs
    if waiting_rows:
        await message.answer(get_text("my_waiting_title", lang, count=len(waiting_rows)))
        for idx, (reg, club) in enumerate(waiting_rows, 1):
            reg_time = reg.registered_at.strftime("%d.%m.%Y") if hasattr(reg.registered_at, "strftime") else ""
            pos = reg.queue_position or 1
            card = (
                f"<b>{idx}. 🎯 {club.name}</b>\n"
                f"   🔢 <b>#{pos}</b>\n"
                f"   🏛 {reg.faculty_name_snap}\n"
                f"   📚 {reg.direction_name_snap}\n"
                f"   🗓 {club.schedule_days} ({club.schedule_time})\n"
                f"   ⏱ {reg_time}\n"
            )
            builder = InlineKeyboardBuilder()
            builder.button(text=get_text("btn_leave_queue", lang), callback_data=f"ask_leave:{reg.id}")
            await message.answer(card, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("ask_leave:"))
async def callback_ask_leave(callback: CallbackQuery, state: FSMContext):
    """Prompt student for confirmation before leaving club/queue."""
    reg_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        reg_repo = RegistrationRepository(session)
        reg = await reg_repo.get_by_id(reg_id)
        if not reg:
            await callback.answer(get_text("no_active_process", lang), show_alert=True)
            return

        club_stmt = select(Club).where(Club.id == reg.club_id)
        club = (await session.execute(club_stmt)).scalar_one_or_none()
        club_name = club.name if club else "To'garak"

    status_name = get_text("status_active_gen", lang) if reg.status == "active" else get_text("status_waiting_gen", lang)
    text = get_text("ask_leave_prompt", lang, club_name=club_name, status_name=status_name)

    await callback.message.edit_text(text=text, reply_markup=get_leave_confirm_keyboard(reg_id, lang))
    await callback.answer()


@router.callback_query(F.data == "cancel_leave")
async def callback_cancel_leave(callback: CallbackQuery, state: FSMContext):
    """Cancel leaving operation."""
    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
    await callback.message.edit_text(get_text("leave_cancelled", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_leave:"))
async def callback_confirm_leave(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Finalize student self-withdrawal and promote next waiting student."""
    reg_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        reg_service = RegistrationService(session=session, bot=bot)
        success, msg, promoted_info = await reg_service.cancel_registration(reg_id)

    if success:
        await callback.message.edit_text(get_text("leave_success", lang))
        await callback.answer()
    else:
        await callback.message.edit_text(f"⚠️ {msg}")
        await callback.answer(msg, show_alert=True)


@router.message(F.text.in_(ABOUT_BUTTONS))
async def cmd_about(message: Message, state: FSMContext):
    """Show information about the university gifted students system."""
    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(message.from_user.id, session, state)
    about_text = get_text("about_text", lang)
    await message.answer(about_text, reply_markup=get_main_menu_keyboard(lang))


@router.message(Command("cancel"))
@router.message(F.text.in_(CANCEL_BUTTONS))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current active FSM operation."""
    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(message.from_user.id, session, state)
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(get_text("no_active_process", lang), reply_markup=get_main_menu_keyboard(lang))
        return

    await state.clear()
    await message.answer(
        get_text("cancel_done", lang),
        reply_markup=get_main_menu_keyboard(lang)
    )
