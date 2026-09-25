from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.models.faculty import Faculty
from src.models.direction import Direction
from src.models.club import Club


def get_faculties_keyboard(faculties: List[Faculty]) -> InlineKeyboardMarkup:
    """Inline keyboard for selecting a faculty."""
    builder = InlineKeyboardBuilder()
    for fac in faculties:
        builder.button(text=f"🏛 {fac.name}", callback_data=f"fac:{fac.id}")
    builder.adjust(1)
    return builder.as_markup()


def get_directions_keyboard(directions: List[Direction], faculty_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard for selecting a direction within a faculty."""
    builder = InlineKeyboardBuilder()
    for direction in directions:
        builder.button(text=f"📚 {direction.name}", callback_data=f"dir:{direction.id}")
    
    # Back button to faculties list
    builder.button(text="⬅️ Fakultetlar ro'yxatiga qaytish", callback_data="back_to_faculties")
    builder.adjust(1)
    return builder.as_markup()


def get_clubs_keyboard(clubs: List[Club], faculty_id: int, direction_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard for selecting a club within a direction."""
    builder = InlineKeyboardBuilder()
    for club in clubs:
        builder.button(text=f"🎯 {club.name}", callback_data=f"club:{club.id}")
    
    # Back button to directions list
    builder.button(text="⬅️ Yo'nalishlar ro'yxatiga qaytish", callback_data=f"back_to_dirs:{faculty_id}")
    builder.adjust(1)
    return builder.as_markup()


def get_club_detail_keyboard(club_id: int, direction_id: int, faculty_id: int) -> InlineKeyboardMarkup:
    """Action buttons for club details: Register or Go Back."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Ro'yxatdan o'tish", callback_data=f"reg_start:{club_id}")
    builder.button(text="⬅️ To'garaklar ro'yxatiga qaytish", callback_data=f"back_to_clubs:{direction_id}:{faculty_id}")
    builder.adjust(1)
    return builder.as_markup()


def get_course_keyboard() -> InlineKeyboardMarkup:
    """Inline buttons to select academic course."""
    builder = InlineKeyboardBuilder()
    builder.button(text="1-kurs", callback_data="course:1")
    builder.button(text="2-kurs", callback_data="course:2")
    builder.button(text="3-kurs", callback_data="course:3")
    builder.button(text="4-kurs", callback_data="course:4")
    builder.button(text="❌ Bekor qilish", callback_data="reg_cancel")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Confirmation keyboard before submitting registration."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, tasdiqlayman", callback_data="confirm_reg:yes")
    builder.button(text="❌ Bekor qilish", callback_data="confirm_reg:no")
    builder.adjust(1)
    return builder.as_markup()
