import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.core.database import AsyncSessionLocal
from src.repositories.faculty_repo import FacultyRepository
from src.repositories.direction_repo import DirectionRepository
from src.repositories.club_repo import ClubRepository
from src.bot.keyboards.inline_user import (
    get_faculties_keyboard,
    get_directions_keyboard,
    get_clubs_keyboard,
    get_club_detail_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name="browse_router")


@router.callback_query(F.data == "back_to_faculties")
async def callback_back_to_faculties(callback: CallbackQuery, state: FSMContext):
    """Return to faculty selection menu."""
    async with AsyncSessionLocal() as session:
        faculty_repo = FacultyRepository(session)
        faculties = await faculty_repo.get_active_faculties()

    text = (
        "🏛 <b>Fakultetlar ro'yxati</b>\n\n"
        "Quyidagi ro'yxatdan o'zingiz tahsil olayotgan fakultetni tanlang:"
    )
    await callback.message.edit_text(text=text, reply_markup=get_faculties_keyboard(faculties))
    await callback.answer()


@router.callback_query(F.data.startswith("fac:"))
async def callback_select_faculty(callback: CallbackQuery, state: FSMContext):
    """Step 2 -> 3: Show directions belonging to the selected faculty."""
    faculty_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        faculty_repo = FacultyRepository(session)
        direction_repo = DirectionRepository(session)

        faculty = await faculty_repo.get_by_id(faculty_id)
        if not faculty:
            await callback.answer("Fakultet topilmadi!", show_alert=True)
            return

        directions = await direction_repo.get_active_by_faculty(faculty_id)

    # Save selected faculty in FSM data for future auto-population
    await state.update_data(faculty_id=faculty.id, faculty_name=faculty.name)

    if not directions:
        text = (
            f"🏛 <b>{faculty.name}</b>\n\n"
            "Ushbu fakultetda hozircha faol ta'lim yo'nalishlari mavjud emas."
        )
        builder_markup = get_directions_keyboard([], faculty_id)
        await callback.message.edit_text(text=text, reply_markup=builder_markup)
        await callback.answer()
        return

    text = (
        f"🏛 <b>Fakultet:</b> {faculty.name}\n\n"
        "⬇️ <i>O'zingiz tahsil olayotgan ta'lim yo'nalishini tanlang:</i>"
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=get_directions_keyboard(directions, faculty_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_dirs:"))
async def callback_back_to_directions(callback: CallbackQuery, state: FSMContext):
    """Return to directions list under the given faculty."""
    faculty_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        faculty_repo = FacultyRepository(session)
        direction_repo = DirectionRepository(session)
        faculty = await faculty_repo.get_by_id(faculty_id)
        directions = await direction_repo.get_active_by_faculty(faculty_id)

    fac_name = faculty.name if faculty else ""
    text = (
        f"🏛 <b>Fakultet:</b> {fac_name}\n\n"
        "⬇️ <i>O'zingiz tahsil olayotgan ta'lim yo'nalishini tanlang:</i>"
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=get_directions_keyboard(directions, faculty_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("dir:"))
async def callback_select_direction(callback: CallbackQuery, state: FSMContext):
    """Step 3 -> 4: Show clubs belonging to the selected direction."""
    direction_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        direction_repo = DirectionRepository(session)
        club_repo = ClubRepository(session)

        direction = await direction_repo.get_by_id(direction_id)
        if not direction:
            await callback.answer("Yo'nalish topilmadi!", show_alert=True)
            return

        clubs = await club_repo.get_active_by_direction(direction_id)

    # Save selected direction in FSM data for future auto-population
    await state.update_data(direction_id=direction.id, direction_name=direction.name)
    user_data = await state.get_data()
    faculty_id = user_data.get("faculty_id", direction.faculty_id)

    if not clubs:
        text = (
            f"📚 <b>Yo'nalish:</b> {direction.name}\n\n"
            "Ushbu yo'nalish bo'yicha hozircha ochiq to'garaklar mavjud emas."
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=get_clubs_keyboard([], faculty_id, direction_id)
        )
        await callback.answer()
        return

    text = (
        f"📚 <b>Yo'nalish:</b> {direction.name}\n\n"
        "⬇️ <i>Quyidagi to'garaklardan birini tanlang va uning shartlari bilan tanishing:</i>"
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=get_clubs_keyboard(clubs, faculty_id, direction_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_clubs:"))
async def callback_back_to_clubs(callback: CallbackQuery, state: FSMContext):
    """Return to clubs list."""
    parts = callback.data.split(":")
    direction_id = int(parts[1])
    faculty_id = int(parts[2])

    async with AsyncSessionLocal() as session:
        direction_repo = DirectionRepository(session)
        club_repo = ClubRepository(session)
        direction = await direction_repo.get_by_id(direction_id)
        clubs = await club_repo.get_active_by_direction(direction_id)

    dir_name = direction.name if direction else ""
    text = (
        f"📚 <b>Yo'nalish:</b> {dir_name}\n\n"
        "⬇️ <i>Quyidagi to'garaklardan birini tanlang va uning shartlari bilan tanishing:</i>"
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=get_clubs_keyboard(clubs, faculty_id, direction_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("club:"))
async def callback_view_club(callback: CallbackQuery, state: FSMContext):
    """Step 5: View full details of the selected club."""
    club_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        club_repo = ClubRepository(session)
        club_data = await club_repo.get_detailed_by_id(club_id)

    if not club_data:
        await callback.answer("To'garak ma'lumotlari topilmadi!", show_alert=True)
        return

    # Update FSM data with full club info
    await state.update_data(
        club_id=club_data["id"],
        club_name=club_data["name"],
        direction_id=club_data["direction_id"],
        direction_name=club_data["direction_name"],
        faculty_id=club_data["faculty_id"],
        faculty_name=club_data["faculty_name"],
        max_capacity=club_data["max_capacity"],
        is_full=club_data["is_full"],
        is_deadline_passed=club_data["is_deadline_passed"],
        waiting_count=club_data["waiting_students_count"]
    )

    active_cnt = club_data["students_count"]
    waiting_cnt = club_data["waiting_students_count"]
    max_cap = club_data["max_capacity"]

    if max_cap > 0:
        if club_data["is_full"]:
            capacity_text = f"<b>{active_cnt}/{max_cap} nafar</b> <i>(Asosiy o'rinlar to'lgan 🔒 | Navbatda: {waiting_cnt} nafar)</i>"
        else:
            free_spots = max_cap - active_cnt
            capacity_text = f"<b>{active_cnt}/{max_cap} nafar</b> <i>({free_spots} ta bo'sh o'rin mavjud)</i>"
    else:
        capacity_text = f"<b>{active_cnt} nafar</b> <i>(Cheklanmagan)</i>"

    # Deadline formatting
    deadline_line = ""
    if club_data.get("registration_deadline"):
        dl = club_data["registration_deadline"]
        dl_str = dl.strftime("%d.%m.%Y %H:%M")
        if club_data["is_deadline_passed"]:
            deadline_line = f"⏳ <b>Ro'yxatdan o'tish muddati:</b> {dl_str} <i>(Muddati tugagan ⛔)</i>\n"
        else:
            deadline_line = f"⏳ <b>Ro'yxatdan o'tish muddati:</b> {dl_str} <i>(Ochiq ✅)</i>\n"

    card_text = (
        f"🎯 <b>TO'GARAK: {club_data['name']}</b>\n\n"
        f"📝 <b>Qisqacha ma'lumot:</b>\n{club_data['description']}\n\n"
        f"🏛 <b>Fakultet:</b> {club_data['faculty_name']}\n"
        f"📚 <b>Yo'nalish:</b> {club_data['direction_name']}\n"
        f"🗓 <b>Mashg'ulot kunlari:</b> {club_data['schedule_days']}\n"
        f"⏰ <b>Vaqti:</b> {club_data['schedule_time']}\n"
        f"📍 <b>Xona / Manzil:</b> {club_data['room_location']}\n"
        f"👨‍🏫 <b>To'garak rahbari:</b> {club_data['leader_name']}\n"
        f"📞 <b>Aloqa:</b> {club_data['leader_contact']}\n"
        f"👥 <b>Qabul qilinganlar:</b> {capacity_text}\n"
        f"{deadline_line}\n"
    )

    if club_data["is_deadline_passed"]:
        card_text += "⛔ <i>Ushbu to'garakka qabul muddati tugaganligi sababli yangi arizalar qabul qilinmaydi.</i>"
    elif club_data["is_full"]:
        card_text += (
            "⚠️ <i>To'garakda asosiy o'rinlar to'lgan. Siz <b>ZAXIRA (NAVBAT)</b>ga yozilishingiz mumkin. "
            "Kimdir chiqib ketsa, navbatdagi talaba avtomatik tarzda qabul qilinadi.</i>"
        )
    else:
        card_text += "<i>To'garakka qatnashishni istasangiz, quyidagi <b>'Ro'yxatdan o'tish'</b> tugmasini bosing:</i>"

    await callback.message.edit_text(
        text=card_text,
        reply_markup=get_club_detail_keyboard(
            club_id=club_data["id"],
            direction_id=club_data["direction_id"],
            faculty_id=club_data["faculty_id"],
            is_expired=club_data["is_deadline_passed"],
            is_full=club_data["is_full"],
            waiting_count=waiting_cnt
        )
    )
    await callback.answer()


@router.callback_query(F.data == "deadline_expired")
async def callback_deadline_expired(callback: CallbackQuery):
    """Handle click on expired deadline button."""
    await callback.answer(
        "⚠️ Ushbu to'garakka ro'yxatdan o'tish muddati tugagan! Yangi arizalar va navbat qabul qilinmaydi.",
        show_alert=True
    )

