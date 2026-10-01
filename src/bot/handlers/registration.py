import re
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from src.core.database import AsyncSessionLocal
from src.repositories.student_repo import StudentRepository
from src.repositories.club_repo import ClubRepository
from src.repositories.registration_repo import RegistrationRepository
from src.services.registration_service import RegistrationService
from src.bot.states import StudentRegistrationState
from src.bot.keyboards.inline_user import get_course_keyboard, get_confirmation_keyboard
from src.bot.keyboards.reply_user import get_phone_keyboard, remove_reply_keyboard, get_main_menu_keyboard
from src.bot.i18n import get_text, get_user_lang

logger = logging.getLogger(__name__)
router = Router(name="registration_router")

# Regex for Uzbekistan and international phone numbers
PHONE_REGEX = re.compile(r"^(\+?998)?[0-9]{9}$")
CANCEL_BUTTONS = ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "/cancel"]


@router.callback_query(F.data.startswith("reg_start:"))
async def callback_start_registration(callback: CallbackQuery, state: FSMContext):
    """Step 6: Initiate student registration form for the selected club in user's language."""
    club_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        student_repo = StudentRepository(session)
        club_repo = ClubRepository(session)
        reg_repo = RegistrationRepository(session)

        club_data = await club_repo.get_detailed_by_id(club_id)
        if not club_data:
            await callback.answer(get_text("club_not_found", lang), show_alert=True)
            return

        # Check deadline
        if club_data.get("is_deadline_passed"):
            await callback.answer(get_text("deadline_alert", lang), show_alert=True)
            return

        # Pre-check: Has this student already registered or waiting?
        existing_student = await student_repo.get_by_telegram_id(callback.from_user.id)
        if existing_student:
            existing_reg = await reg_repo.get_by_student_and_club(existing_student.id, club_id)
            if existing_reg:
                if existing_reg.status == "active":
                    await callback.answer(get_text("already_registered", lang), show_alert=True)
                    return
                elif existing_reg.status == "waiting":
                    pos_str = f" (#{existing_reg.queue_position})" if existing_reg.queue_position else ""
                    await callback.answer(get_text("already_in_queue", lang, pos=pos_str), show_alert=True)
                    return

    is_full = club_data.get("is_full", False)
    waiting_cnt = club_data.get("waiting_students_count", 0)

    # Update state data with club, auto-populated faculty & direction, and language
    await state.update_data(
        club_id=club_data["id"],
        club_name=club_data["name"],
        direction_id=club_data["direction_id"],
        direction_name=club_data["direction_name"],
        faculty_id=club_data["faculty_id"],
        faculty_name=club_data["faculty_name"],
        is_full=is_full,
        next_queue_pos=waiting_cnt + 1,
        user_lang=lang
    )

    await state.set_state(StudentRegistrationState.waiting_for_full_name)

    if is_full:
        intro_text = get_text("reg_intro_waiting", lang, club=club_data["name"], num=waiting_cnt + 1)
    else:
        intro_text = get_text("reg_intro_active", lang, club=club_data["name"])

    await callback.message.answer(intro_text)
    await callback.answer()


@router.message(StudentRegistrationState.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Process and validate student's full name."""
    data = await state.get_data()
    lang = data.get("user_lang", "uz")

    if message.text in CANCEL_BUTTONS:
        await state.clear()
        await message.answer(get_text("reg_cancelled", lang), reply_markup=get_main_menu_keyboard(lang))
        return

    full_name = message.text.strip()
    words = full_name.split()
    if len(words) < 2 or len(full_name) < 5 or len(full_name) > 100:
        await message.answer(get_text("name_validation_err", lang))
        return

    await state.update_data(full_name=full_name)
    await state.set_state(StudentRegistrationState.waiting_for_course)

    await message.answer(
        get_text("select_course_prompt", lang, full_name=full_name),
        reply_markup=get_course_keyboard(lang)
    )


@router.callback_query(F.data.startswith("course:"))
async def process_course_selection(callback: CallbackQuery, state: FSMContext):
    """Process course level selection."""
    data = await state.get_data()
    lang = data.get("user_lang", "uz")

    course_level = int(callback.data.split(":")[1])
    await state.update_data(course_level=course_level)
    await state.set_state(StudentRegistrationState.waiting_for_phone)

    await callback.message.delete()
    await callback.message.answer(
        get_text("send_phone_prompt", lang),
        reply_markup=get_phone_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "reg_cancel")
async def process_reg_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel registration via inline button."""
    data = await state.get_data()
    lang = data.get("user_lang", "uz")

    await state.clear()
    await callback.message.edit_text(get_text("reg_cancelled", lang))
    await callback.answer()


@router.message(StudentRegistrationState.waiting_for_phone)
async def process_phone_number(message: Message, state: FSMContext):
    """Process student's phone number either via Contact button or text input."""
    data = await state.get_data()
    lang = data.get("user_lang", "uz")

    if message.text in CANCEL_BUTTONS:
        await state.clear()
        await message.answer(
            get_text("reg_cancelled", lang),
            reply_markup=remove_reply_keyboard()
        )
        return

    phone_number = None

    # Option 1: Shared Telegram contact
    if message.contact:
        phone_number = message.contact.phone_number
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
    # Option 2: Written text
    elif message.text:
        raw_text = message.text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if PHONE_REGEX.match(raw_text):
            if not raw_text.startswith("+"):
                raw_text = f"+{raw_text}" if raw_text.startswith("998") else f"+998{raw_text}"
            phone_number = raw_text

    if not phone_number:
        await message.answer(
            get_text("phone_validation_err", lang),
            reply_markup=get_phone_keyboard(lang)
        )
        return

    # Auto-captured Telegram username from sender
    username = message.from_user.username

    await state.update_data(
        phone_number=phone_number,
        telegram_username=username
    )
    await state.set_state(StudentRegistrationState.waiting_for_confirmation)

    data = await state.get_data()

    # Step 9: Re-display all data for student confirmation
    username_display = f"@{username}" if username else "-"
    review_card = get_text(
        "review_card",
        lang,
        full_name=data.get("full_name"),
        faculty_name=data.get("faculty_name"),
        direction_name=data.get("direction_name"),
        club_name=data.get("club_name"),
        course_level=data.get("course_level"),
        phone_number=phone_number,
        telegram_username=username_display
    )

    # First remove reply keyboard
    await message.answer(get_text("data_received", lang), reply_markup=remove_reply_keyboard())
    # Then present review card
    await message.answer(
        text=review_card,
        reply_markup=get_confirmation_keyboard(lang)
    )


@router.callback_query(F.data.startswith("confirm_reg:"))
async def process_final_confirmation(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Step 10, 11, 12, 16: Handle submission, duplicate prevention, and admin notification."""
    data = await state.get_data()
    lang = data.get("user_lang", "uz")
    action = callback.data.split(":")[1]

    if action == "no":
        await state.clear()
        await callback.message.edit_text(get_text("reg_cancelled", lang))
        await callback.answer()
        return

    club_id = data.get("club_id")
    full_name = data.get("full_name")
    course_level = data.get("course_level")
    phone_number = data.get("phone_number")
    telegram_username = data.get("telegram_username") or callback.from_user.username

    if not all([club_id, full_name, course_level, phone_number]):
        await callback.answer(get_text("no_active_process", lang), show_alert=True)
        await state.clear()
        return

    async with AsyncSessionLocal() as session:
        reg_service = RegistrationService(session=session, bot=bot)
        success, message_text, registration = await reg_service.register_student(
            telegram_id=callback.from_user.id,
            full_name=full_name,
            phone_number=phone_number,
            club_id=club_id,
            course_level=course_level,
            telegram_username=telegram_username,
            language=lang
        )

    await state.clear()

    if success:
        if registration and registration.status == "waiting":
            queue_card = get_text(
                "reg_success_waiting",
                lang,
                club=data.get("club_name"),
                num=registration.queue_position
            )
            await callback.message.edit_text(text=queue_card)
            await callback.answer()
        else:
            success_card = get_text(
                "reg_success_active",
                lang,
                club=data.get("club_name")
            )
            await callback.message.edit_text(text=success_card)
            await callback.answer()
    else:
        await callback.message.edit_text(f"⚠️ <b>{message_text}</b>")
        await callback.answer(message_text, show_alert=True)
