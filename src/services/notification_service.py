import logging
from typing import Optional, List, Union
from datetime import datetime
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    async def notify_admins(
        bot: Optional[Bot],
        full_name: str,
        phone_number: str,
        telegram_username: Optional[str],
        faculty_name: str,
        direction_name: str,
        club_name: str,
        course_level: int,
        channel_id: Optional[str] = None,
        additional_chat_ids: Optional[List[int]] = None
    ):
        """
        Send automated Telegram notification to management channel and administrators
        when a gifted student registers.
        """
        if not bot:
            logger.warning("Bot instance not provided to NotificationService.")
            return

        # Target destinations
        destinations = set()
        
        # 1. Primary Management Channel
        primary_channel = channel_id or settings.ADMIN_CHANNEL_ID
        if primary_channel and primary_channel.strip():
            destinations.add(primary_channel.strip())

        # 2. Admin Chat IDs from .env
        for cid in settings.admin_chat_id_list:
            destinations.add(cid)

        # 3. Additional Admin Chat IDs from DB
        if additional_chat_ids:
            for cid in additional_chat_ids:
                if cid:
                    destinations.add(cid)

        if not destinations:
            logger.info("No admin chat or channel IDs configured for registration notifications.")
            return

        username_text = f"@{telegram_username}" if telegram_username else "Mavjud emas"
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")

        message_text = (
            "🔔 <b>YANGI IQTIDORLI TALABA RO'YXATDAN O'TDI!</b>\n\n"
            f"👤 <b>F.I.Sh:</b> {full_name}\n"
            f"🏛 <b>Fakultet:</b> {faculty_name}\n"
            f"📚 <b>Ta'lim Yo'nalishi:</b> {direction_name}\n"
            f"🎯 <b>To'garak:</b> {club_name}\n"
            f"🎓 <b>Kurs:</b> {course_level}-kurs\n"
            f"📞 <b>Telefon:</b> {phone_number}\n"
            f"💬 <b>Telegram:</b> {username_text}\n"
            f"⏱ <b>Vaqt:</b> {current_time}\n\n"
            "<i>Ushbu ma'lumotlar avtomatik tarzda universitet ma'lumotlar bazasiga kiritildi.</i>\n\n"
            "#iqtidorli_talaba #ariza"
        )

        # Quick action buttons for administrators
        keyboard_buttons = []
        if telegram_username:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text="💬 Telegram orqali yozish",
                    url=f"https://t.me/{telegram_username.lstrip('@')}"
                )
            ])

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons) if keyboard_buttons else None

        for dest in destinations:
            try:
                await bot.send_message(
                    chat_id=dest,
                    text=message_text,
                    parse_mode="HTML",
                    reply_markup=markup
                )
                logger.info(f"Notification successfully sent to {dest}")
            except Exception as e:
                logger.error(f"Failed to send notification to destination {dest}: {e}")

    @staticmethod
    async def send_test_notification(bot: Optional[Bot], target_chat: Union[str, int]) -> bool:
        """Send a test ping message to the specified channel/chat to confirm bot permissions."""
        if not bot:
            return False
        try:
            await bot.send_message(
                chat_id=target_chat,
                text=(
                    "✅ <b>UNIVERSITET IQTIDORLI TALABALAR BOTI: SINOV XABARI</b>\n\n"
                    "Ushbu kanal/guruh yangi talabalar ro'yxatdan o'tganda xabarnomalarni "
                    "qabul qilish uchun muvaffaqiyatli ulandi!"
                ),
                parse_mode="HTML"
            )
            return True
        except Exception as e:
            logger.error(f"Test notification to {target_chat} failed: {e}")
            return False
