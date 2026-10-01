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
from src.bot.i18n import get_text, get_user_lang

logger = logging.getLogger(__name__)
router = Router(name="browse_router")


@router.callback_query(F.data == "back_to_faculties")
async def callback_back_to_faculties(callback: CallbackQuery, state: FSMContext):
    """Return to faculty selection menu."""
    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        faculty_repo = FacultyRepository(session)
        faculties = await faculty_repo.get_active_faculties()

    text = get_text("catalog_faculties_title", lang)
    await callback.message.edit_text(text=text, reply_markup=get_faculties_keyboard(faculties, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("fac:"))
async def callback_select_faculty(callback: CallbackQuery, state: FSMContext):
    """Step 2 -> 3: Show directions belonging to the selected faculty."""
    faculty_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        faculty_repo = FacultyRepository(session)
        direction_repo = DirectionRepository(session)

        faculty = await faculty_repo.get_by_id(faculty_id)
        if not faculty:
            await callback.answer(get_text("faculty_not_found", lang), show_alert=True)
            return

        directions = await direction_repo.get_active_by_faculty(faculty_id)

    # Save selected faculty in FSM data for future auto-population
    await state.update_data(faculty_id=faculty.id, faculty_name=faculty.name)

    if not directions:
        text = get_text("no_directions", lang, faculty_name=faculty.name)
        builder_markup = get_directions_keyboard([], faculty_id, lang)
        await callback.message.edit_text(text=text, reply_markup=builder_markup)
        await callback.answer()
        return

    text = get_text("select_direction_prompt", lang, faculty_name=faculty.name)
    await callback.message.edit_text(
        text=text,
        reply_markup=get_directions_keyboard(directions, faculty_id, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_dirs:"))
async def callback_back_to_directions(callback: CallbackQuery, state: FSMContext):
    """Return to directions list under the given faculty."""
    faculty_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        faculty_repo = FacultyRepository(session)
        direction_repo = DirectionRepository(session)
        faculty = await faculty_repo.get_by_id(faculty_id)
        directions = await direction_repo.get_active_by_faculty(faculty_id)

    fac_name = faculty.name if faculty else ""
    text = get_text("select_direction_prompt", lang, faculty_name=fac_name)
    await callback.message.edit_text(
        text=text,
        reply_markup=get_directions_keyboard(directions, faculty_id, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("dir:"))
async def callback_select_direction(callback: CallbackQuery, state: FSMContext):
    """Step 3 -> 4: Show clubs belonging to the selected direction."""
    direction_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        direction_repo = DirectionRepository(session)
        club_repo = ClubRepository(session)

        direction = await direction_repo.get_by_id(direction_id)
        if not direction:
            await callback.answer(get_text("direction_not_found", lang), show_alert=True)
            return

        clubs = await club_repo.get_active_by_direction(direction_id)

    await state.update_data(direction_id=direction.id, direction_name=direction.name)
    user_data = await state.get_data()
    faculty_id = user_data.get("faculty_id", direction.faculty_id)

    if not clubs:
        text = get_text("no_clubs", lang, direction_name=direction.name)
        await callback.message.edit_text(
            text=text,
            reply_markup=get_clubs_keyboard([], faculty_id, direction_id, lang)
        )
        await callback.answer()
        return

    text = get_text("select_club_prompt", lang, direction_name=direction.name)
    await callback.message.edit_text(
        text=text,
        reply_markup=get_clubs_keyboard(clubs, faculty_id, direction_id, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_clubs:"))
async def callback_back_to_clubs(callback: CallbackQuery, state: FSMContext):
    """Return to clubs list."""
    parts = callback.data.split(":")
    direction_id = int(parts[1])
    faculty_id = int(parts[2])

    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        direction_repo = DirectionRepository(session)
        club_repo = ClubRepository(session)
        direction = await direction_repo.get_by_id(direction_id)
        clubs = await club_repo.get_active_by_direction(direction_id)

    dir_name = direction.name if direction else ""
    text = get_text("select_club_prompt", lang, direction_name=dir_name)
    await callback.message.edit_text(
        text=text,
        reply_markup=get_clubs_keyboard(clubs, faculty_id, direction_id, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("club:"))
async def callback_view_club(callback: CallbackQuery, state: FSMContext):
    """Step 5: View full details of the selected club in user's language."""
    club_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
        club_repo = ClubRepository(session)
        club_data = await club_repo.get_detailed_by_id(club_id)

    if not club_data:
        await callback.answer(get_text("club_not_found", lang), show_alert=True)
        return

    # Update FSM data
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

    # Capacity string localized
    if max_cap > 0:
        if club_data["is_full"]:
            if lang == "ru":
                capacity_info = f"<b>{active_cnt}/{max_cap}</b> <i>(Основные места заполнены 🔒)</i>"
            elif lang == "en":
                capacity_info = f"<b>{active_cnt}/{max_cap}</b> <i>(Main spots full 🔒)</i>"
            else:
                capacity_info = f"<b>{active_cnt}/{max_cap}</b> <i>(Asosiy o'rinlar to'lgan 🔒)</i>"
        else:
            free_spots = max_cap - active_cnt
            if lang == "ru":
                capacity_info = f"<b>{active_cnt}/{max_cap}</b> <i>(Свободно: {free_spots})</i>"
            elif lang == "en":
                capacity_info = f"<b>{active_cnt}/{max_cap}</b> <i>(Available: {free_spots})</i>"
            else:
                capacity_info = f"<b>{active_cnt}/{max_cap}</b> <i>({free_spots} ta bo'sh o'rin mavjud)</i>"
    else:
        if lang == "ru":
            capacity_info = f"<b>{active_cnt}</b> <i>(Без ограничений)</i>"
        elif lang == "en":
            capacity_info = f"<b>{active_cnt}</b> <i>(Unlimited)</i>"
        else:
            capacity_info = f"<b>{active_cnt} nafar</b> <i>(Cheklanmagan)</i>"

    # Waiting info
    if waiting_cnt > 0:
        if lang == "ru":
            waiting_info = f"<b>{waiting_cnt} человек</b>"
        elif lang == "en":
            waiting_info = f"<b>{waiting_cnt} students</b>"
        else:
            waiting_info = f"<b>{waiting_cnt} nafar</b>"
    else:
        if lang == "ru":
            waiting_info = "<i>Нет очереди</i>"
        elif lang == "en":
            waiting_info = "<i>No queue</i>"
        else:
            waiting_info = "<i>Navbat yo'q</i>"

    # Deadline formatting
    deadline_line = ""
    if club_data.get("registration_deadline"):
        dl = club_data["registration_deadline"]
        dl_str = dl.strftime("%d.%m.%Y %H:%M")
        if club_data["is_deadline_passed"]:
            if lang == "ru":
                deadline_line = f"⏳ <b>Срок регистрации:</b> {dl_str} <i>(Срок истек ⛔)</i>\n"
            elif lang == "en":
                deadline_line = f"⏳ <b>Registration deadline:</b> {dl_str} <i>(Expired ⛔)</i>\n"
            else:
                deadline_line = f"⏳ <b>Ro'yxatdan o'tish muddati:</b> {dl_str} <i>(Muddati tugagan ⛔)</i>\n"
        else:
            if lang == "ru":
                deadline_line = f"⏳ <b>Срок регистрации:</b> {dl_str} <i>(Открыто ✅)</i>\n"
            elif lang == "en":
                deadline_line = f"⏳ <b>Registration deadline:</b> {dl_str} <i>(Open ✅)</i>\n"
            else:
                deadline_line = f"⏳ <b>Ro'yxatdan o'tish muddati:</b> {dl_str} <i>(Ochiq ✅)</i>\n"

    card_text = get_text(
        "club_detail_card",
        lang,
        name=club_data["name"],
        faculty_name=club_data["faculty_name"],
        direction_name=club_data["direction_name"],
        description=club_data["description"],
        schedule_days=club_data["schedule_days"],
        schedule_time=club_data["schedule_time"],
        room_location=club_data["room_location"],
        leader_name=club_data["leader_name"],
        leader_contact=club_data["leader_contact"],
        capacity_info=capacity_info,
        waiting_info=waiting_info,
        deadline_info=deadline_line
    )

    await callback.message.edit_text(
        text=card_text,
        reply_markup=get_club_detail_keyboard(
            club_id=club_data["id"],
            direction_id=club_data["direction_id"],
            faculty_id=club_data["faculty_id"],
            is_expired=club_data["is_deadline_passed"],
            is_full=club_data["is_full"],
            waiting_count=waiting_cnt,
            lang=lang
        )
    )
    await callback.answer()


@router.callback_query(F.data == "deadline_expired")
async def callback_deadline_expired(callback: CallbackQuery, state: FSMContext):
    """Handle click on expired deadline button."""
    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(callback.from_user.id, session, state)
    await callback.answer(get_text("deadline_alert", lang), show_alert=True)
