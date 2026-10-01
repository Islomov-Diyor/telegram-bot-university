from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from src.bot.i18n import get_text


def get_phone_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Reply keyboard requesting user phone number contact or cancel."""
    button_phone = KeyboardButton(text=get_text("btn_share_phone", lang), request_contact=True)
    button_cancel = KeyboardButton(text=get_text("btn_cancel", lang))
    return ReplyKeyboardMarkup(
        keyboard=[[button_phone], [button_cancel]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_main_menu_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Persistent bottom keyboard for quick access localized by lang."""
    btn_catalog = KeyboardButton(text=get_text("btn_catalog", lang))
    btn_my_clubs = KeyboardButton(text=get_text("btn_my_clubs", lang))
    btn_about = KeyboardButton(text=get_text("btn_about", lang))
    btn_lang = KeyboardButton(text=get_text("btn_lang", lang))
    return ReplyKeyboardMarkup(
        keyboard=[
            [btn_catalog],
            [btn_my_clubs, btn_about],
            [btn_lang]
        ],
        resize_keyboard=True
    )


def remove_reply_keyboard() -> ReplyKeyboardRemove:
    """Remove reply keyboard."""
    return ReplyKeyboardRemove()
