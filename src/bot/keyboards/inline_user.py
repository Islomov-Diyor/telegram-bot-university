from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.models.faculty import Faculty
from src.models.direction import Direction
from src.models.club import Club
from src.bot.i18n import get_text


def get_faculties_keyboard(faculties: List[Faculty], lang: str = "uz") -> InlineKeyboardMarkup:
    """Inline keyboard for selecting a faculty."""
    builder = InlineKeyboardBuilder()
    for fac in faculties:
        builder.button(text=f"🏛 {fac.name}", callback_data=f"fac:{fac.id}")
    builder.adjust(1)
    return builder.as_markup()


def get_directions_keyboard(directions: List[Direction], faculty_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Inline keyboard for selecting a direction within a faculty."""
    builder = InlineKeyboardBuilder()
    for direction in directions:
        builder.button(text=f"📚 {direction.name}", callback_data=f"dir:{direction.id}")
    
    # Localized back button to faculties list
    builder.button(text=get_text("back_to_faculties", lang), callback_data="back_to_faculties")
    builder.adjust(1)
    return builder.as_markup()


def get_clubs_keyboard(clubs: List[Club], faculty_id: int, direction_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Inline keyboard for selecting a club within a direction."""
    builder = InlineKeyboardBuilder()
    for club in clubs:
        builder.button(text=f"🎯 {club.name}", callback_data=f"club:{club.id}")
    
    # Localized back button to directions list
    builder.button(text=get_text("back_to_directions", lang), callback_data=f"back_to_dirs:{faculty_id}")
    builder.adjust(1)
    return builder.as_markup()


def get_club_detail_keyboard(
    club_id: int,
    direction_id: int,
    faculty_id: int,
    is_expired: bool = False,
    is_full: bool = False,
    waiting_count: int = 0,
    lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Action buttons for club details: Register, Join Queue, or Deadline Expired."""
    builder = InlineKeyboardBuilder()

    if is_expired:
        builder.button(text=get_text("btn_deadline_expired", lang), callback_data="deadline_expired")
    elif is_full:
        builder.button(text=get_text("btn_join_queue", lang, num=waiting_count + 1), callback_data=f"reg_start:{club_id}")
    else:
        builder.button(text=get_text("btn_register", lang), callback_data=f"reg_start:{club_id}")

    builder.button(text=get_text("back_to_clubs", lang), callback_data=f"back_to_clubs:{direction_id}:{faculty_id}")
    builder.adjust(1)
    return builder.as_markup()


def get_course_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Inline buttons to select academic course."""
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("course_1", lang), callback_data="course:1")
    builder.button(text=get_text("course_2", lang), callback_data="course:2")
    builder.button(text=get_text("course_3", lang), callback_data="course:3")
    builder.button(text=get_text("course_4", lang), callback_data="course:4")
    builder.button(text=get_text("btn_cancel", lang), callback_data="reg_cancel")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_confirmation_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Confirmation keyboard before submitting registration."""
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("btn_confirm", lang), callback_data="confirm_reg:yes")
    builder.button(text=get_text("btn_cancel", lang), callback_data="confirm_reg:no")
    builder.adjust(1)
    return builder.as_markup()


def get_leave_confirm_keyboard(registration_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Confirmation keyboard before withdrawing/cancelling a registration."""
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("btn_confirm_leave", lang), callback_data=f"confirm_leave:{registration_id}")
    builder.button(text=get_text("btn_cancel", lang), callback_data="cancel_leave")
    builder.adjust(1)
    return builder.as_markup()
