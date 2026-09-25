from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard requesting user phone number contact or cancel."""
    button_phone = KeyboardButton(text="📞 Telefon raqamimni ulashish", request_contact=True)
    button_cancel = KeyboardButton(text="❌ Bekor qilish")
    return ReplyKeyboardMarkup(
        keyboard=[[button_phone], [button_cancel]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Persistent bottom keyboard for quick access."""
    btn_catalog = KeyboardButton(text="🏛 To'garaklar katalogi")
    btn_my_clubs = KeyboardButton(text="📋 Mening to'garaklarim")
    btn_about = KeyboardButton(text="ℹ️ Bot haqida")
    return ReplyKeyboardMarkup(
        keyboard=[
            [btn_catalog],
            [btn_my_clubs, btn_about]
        ],
        resize_keyboard=True
    )


def remove_reply_keyboard() -> ReplyKeyboardRemove:
    """Remove reply keyboard."""
    return ReplyKeyboardRemove()
