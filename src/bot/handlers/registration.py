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

logger = logging.getLogger(__name__)
router = Router(name="registration_router")

# Regex for Uzbekistan phone numbers
PHONE_REGEX = re.compile(r"^(\+?998)?[0-9]{9}$")


@router.callback_query(F.data.startswith("reg_start:"))
async def callback_start_registration(callback: CallbackQuery, state: FSMContext):
    """Step 6: Initiate student registration form for the selected club."""
    club_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        student_repo = StudentRepository(session)
        club_repo = ClubRepository(session)
        reg_repo = RegistrationRepository(session)

        club_data = await club_repo.get_detailed_by_id(club_id)
        if not club_data:
            await callback.answer("To'garak topilmadi!", show_alert=True)
            return

        # Pre-check: Has this student already registered?
        existing_student = await student_repo.get_by_telegram_id(callback.from_user.id)
        if existing_student:
            is_reg = await reg_repo.is_already_registered(existing_student.id, club_id)
            if is_reg:
                await callback.answer(
                    "⚠️ Siz allaqachon ushbu to'garakka a'zo bo'lgansiz!",
                    show_alert=True
                )
                return

    # Update state data with club and auto-populated faculty & direction
    await state.update_data(
        club_id=club_data["id"],
        club_name=club_data["name"],
        direction_id=club_data["direction_id"],
        direction_name=club_data["direction_name"],
        faculty_id=club_data["faculty_id"],
        faculty_name=club_data["faculty_name"]
    )

    await state.set_state(StudentRegistrationState.waiting_for_full_name)
    await callback.message.answer(
        f"📝 <b>'{club_data['name']}' to'garagiga ro'yxatdan o'tish</b>\n\n"
        "1/3. Iltimos, to'liq <b>ism-familiyangizni</b> kiriting:\n"
        "<i>(Masalan: Saidov Jasur Akmal o'g'li)</i>"
    )
    await callback.answer()


@router.message(StudentRegistrationState.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Process and validate student's full name."""
    if message.text in ["❌ Bekor qilish", "/cancel"]:
        await state.clear()
        await message.answer("❌ Ro'yxatdan o'tish bekor qilindi.", reply_markup=get_main_menu_keyboard())
        return

    full_name = message.text.strip()
    words = full_name.split()
    if len(words) < 2 or len(full_name) < 5 or len(full_name) > 100:
        await message.answer(
            "⚠️ Iltimos, ism va familiyangizni to'liq kiriting!\n"
            "<i>(Kamida 2 ta so'z, masalan: Saidov Jasur)</i>"
        )
        return

    await state.update_data(full_name=full_name)
    await state.set_state(StudentRegistrationState.waiting_for_course)

    await message.answer(
        f"Rahmat, <b>{full_name}</b>!\n\n"
        "2/3. Nechanchi kursda tahsil olasiz? Quyidagilardan tanlang:",
        reply_markup=get_course_keyboard()
    )


@router.callback_query(F.data.startswith("course:"))
async def process_course_selection(callback: CallbackQuery, state: FSMContext):
    """Process course level selection."""
    course_level = int(callback.data.split(":")[1])
    await state.update_data(course_level=course_level)
    await state.set_state(StudentRegistrationState.waiting_for_phone)

    await callback.message.delete()
    await callback.message.answer(
        "3/3. 📞 <b>Telefon raqamingizni yuboring:</b>\n\n"
        "Quyidagi <b>'Telefon raqamimni ulashish'</b> tugmasini bosing yoki "
        "qo'lda yozib yuboring (Masalan: <code>+998901234567</code>):",
        reply_markup=get_phone_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "reg_cancel")
async def process_reg_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel registration via inline button."""
    await state.clear()
    await callback.message.edit_text("❌ Ro'yxatdan o'tish bekor qilindi.")
    await callback.answer()


@router.message(StudentRegistrationState.waiting_for_phone)
async def process_phone_number(message: Message, state: FSMContext):
    """Process student's phone number either via Contact button or text input."""
    if message.text in ["❌ Bekor qilish", "/cancel"]:
        await state.clear()
        await message.answer(
            "❌ Ro'yxatdan o'tish bekor qilindi.",
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
            "⚠️ Telefon raqam noto'g'ri kiritildi!\n"
            "Iltimos, pastdagi <b>'Telefon raqamimni ulashish'</b> tugmasidan foydalaning "
            "yoki raqamingizni <code>+998901234567</code> formatida yozing.",
            reply_markup=get_phone_keyboard()
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
    username_display = f"@{username}" if username else "Mavjud emas"
    review_card = (
        "📋 <b>Arizangiz ma'lumotlarini tekshiring:</b>\n\n"
        f"👤 <b>F.I.Sh:</b> {data.get('full_name')}\n"
        f"🏛 <b>Fakultet:</b> {data.get('faculty_name')}\n"
        f"📚 <b>Ta'lim yo'nalishi:</b> {data.get('direction_name')}\n"
        f"🎯 <b>To'garak:</b> {data.get('club_name')}\n"
        f"🎓 <b>Kurs:</b> {data.get('course_level')}-kurs\n"
        f"📞 <b>Telefon:</b> {phone_number}\n"
        f"💬 <b>Telegram:</b> {username_display}\n\n"
        "<i>Barcha ma'lumotlar to'g'rimi? Tasdiqlash uchun quyidagi tugmani bosing:</i>"
    )

    # First remove the reply keyboard
    await message.answer("Ma'lumotlar qabul qilindi.", reply_markup=remove_reply_keyboard())
    # Then present the confirmation card with inline buttons
    await message.answer(
        text=review_card,
        reply_markup=get_confirmation_keyboard()
    )


@router.callback_query(F.data.startswith("confirm_reg:"))
async def process_final_confirmation(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Step 10, 11, 12, 16: Handle submission, duplicate prevention, and admin notification."""
    action = callback.data.split(":")[1]

    if action == "no":
        await state.clear()
        await callback.message.edit_text("❌ Ariza bekor qilindi.")
        await callback.answer()
        return

    data = await state.get_data()
    club_id = data.get("club_id")
    full_name = data.get("full_name")
    course_level = data.get("course_level")
    phone_number = data.get("phone_number")
    telegram_username = data.get("telegram_username") or callback.from_user.username

    if not all([club_id, full_name, course_level, phone_number]):
        await callback.answer("Ma'lumotlar to'liq emas. Iltimos qaytadan /start bosing.", show_alert=True)
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
            telegram_username=telegram_username
        )

    await state.clear()

    if success:
        # Step 12: Success message
        success_card = (
            "🎉 <b>TABRIKLAYMIZ! RO'YXATDAN O'TISH MUVAFFAQIYATLI YAKUNLANDI!</b>\n\n"
            f"Siz <b>'{data.get('club_name')}'</b> to'garagiga a'zo bo'ldingiz.\n\n"
            "📌 <b>Eslatma:</b> To'garak rahbari yaqin vaqt ichida siz bilan bog'lanadi. "
            "Mashg'ulotlarga o'z vaqtida kelishingizni so'raymiz.\n\n"
            "<i>Yana boshqa to'garaklar bilan tanishish uchun /start ni bosing.</i>"
        )
        await callback.message.edit_text(text=success_card)
        await callback.answer("Muvaffaqiyatli ro'yxatdan o'tdingiz!", show_alert=False)
    else:
        # Step 11: Duplicate rejection or error message
        await callback.message.edit_text(
            f"⚠️ <b>{message_text}</b>\n\n"
            "To'garaklar katalogiga qaytish uchun /start ni bosing."
        )
        await callback.answer(message_text, show_alert=True)
