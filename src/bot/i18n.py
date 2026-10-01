from typing import Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

LANGUAGES: Dict[str, str] = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

DEFAULT_LANGUAGE = "uz"

MESSAGES: Dict[str, Dict[str, str]] = {
    # 1. Language & Welcome
    "choose_language": {
        "uz": (
            "👋 <b>Assalomu alaykum! / Здравствуйте! / Welcome!</b>\n\n"
            "🌐 Iltimos, muloqot tilini tanlang:\n"
            "Пожалуйста, выберите язык:\n"
            "Please select your language:"
        ),
        "ru": (
            "👋 <b>Assalomu alaykum! / Здравствуйте! / Welcome!</b>\n\n"
            "🌐 Пожалуйста, выберите язык общения:\n"
            "Iltimos, muloqot tilini tanlang:\n"
            "Please select your language:"
        ),
        "en": (
            "👋 <b>Assalomu alaykum! / Здравствуйте! / Welcome!</b>\n\n"
            "🌐 Please select your language:\n"
            "Iltimos, muloqot tilini tanlang:\n"
            "Пожалуйста, выберите язык:"
        ),
    },
    "lang_changed": {
        "uz": "✅ Muloqot tili muvaffaqiyatli tanlandi: <b>{lang_name}</b>",
        "ru": "✅ Язык общения успешно выбран: <b>{lang_name}</b>",
        "en": "✅ Language successfully selected: <b>{lang_name}</b>",
    },
    "welcome_title": {
        "uz": (
            "👋 <b>Assalomu alaykum, hurmatli talaba!</b>\n\n"
            "🏛 <b>UNIVERSITET IQTIDORLI TALABALAR BOTI</b>ga xush kelibsiz!\n\n"
            "Ushbu bot orqali universitetimizdagi barcha ilmiy, ijodiy va fan to'garaklari "
            "haqida to'liq ma'lumot olishingiz hamda o'zingiz qiziqqan to'garakka online a'zo bo'lishingiz mumkin.\n\n"
            "⬇️ <i>Boshlash uchun quyidagi ro'yxatdan o'zingiz tahsil olayotgan fakultetni tanlang:</i>"
        ),
        "ru": (
            "👋 <b>Здравствуйте, уважаемый студент!</b>\n\n"
            "🏛 Добро пожаловать в <b>БОТ ОДАРЕННЫХ СТУДЕНТОВ УНИВЕРСИТЕТА</b>!\n\n"
            "Через этот бот вы можете получить подробную информацию обо всех научных, творческих "
            "и предметных кружках нашего университета, а также записаться в интересующий кружок онлайн.\n\n"
            "⬇️ <i>Для начала выберите факультет, на котором вы обучаетесь:</i>"
        ),
        "en": (
            "👋 <b>Welcome, dear student!</b>\n\n"
            "🏛 Welcome to the <b>UNIVERSITY GIFTED STUDENTS BOT</b>!\n\n"
            "Through this bot, you can get full information about all scientific, creative, "
            "and academic clubs in our university and register online.\n\n"
            "⬇️ <i>To begin, please select your faculty from the list below:</i>"
        ),
    },
    "no_faculties": {
        "uz": "Assalomu alaykum!\n\nHozirda tizimda faol fakultetlar yoki to'garaklar mavjud emas. Iltimos, keyinroq qayta tekshiring.",
        "ru": "Здравствуйте!\n\nВ настоящее время в системе нет активных факультетов или кружков. Пожалуйста, проверьте позже.",
        "en": "Hello!\n\nCurrently, there are no active faculties or clubs in the system. Please check back later.",
    },

    # 2. Main Menu Reply Buttons
    "btn_catalog": {
        "uz": "🏛 To'garaklar katalogi",
        "ru": "🏛 Каталог кружков",
        "en": "🏛 Clubs catalog",
    },
    "btn_my_clubs": {
        "uz": "📋 Mening to'garaklarim",
        "ru": "📋 Мои кружки",
        "en": "📋 My clubs",
    },
    "btn_about": {
        "uz": "ℹ️ Bot haqida",
        "ru": "ℹ️ О боте",
        "en": "ℹ️ About bot",
    },
    "btn_lang": {
        "uz": "🌐 Til / Language",
        "ru": "🌐 Язык / Language",
        "en": "🌐 Language / Til",
    },
    "btn_share_phone": {
        "uz": "📞 Telefon raqamimni ulashish",
        "ru": "📞 Поделиться номером телефона",
        "en": "📞 Share my phone number",
    },
    "btn_cancel": {
        "uz": "❌ Bekor qilish",
        "ru": "❌ Отмена",
        "en": "❌ Cancel",
    },

    # 3. Catalog & Browsing
    "catalog_faculties_title": {
        "uz": "🏛 <b>Fakultetlar ro'yxati</b>\n\nQuyidagi ro'yxatdan o'zingiz tahsil olayotgan fakultetni tanlang:",
        "ru": "🏛 <b>Список факультетов</b>\n\nВыберите ваш факультет из списка ниже:",
        "en": "🏛 <b>Faculties list</b>\n\nSelect your faculty from the list below:",
    },
    "faculty_not_found": {
        "uz": "Fakultet topilmadi!",
        "ru": "Факультет не найден!",
        "en": "Faculty not found!",
    },
    "no_directions": {
        "uz": "🏛 <b>{faculty_name}</b>\n\nUshbu fakultetda hozircha faol ta'lim yo'nalishlari mavjud emas.",
        "ru": "🏛 <b>{faculty_name}</b>\n\nНа этом факультете пока нет активных направлений обучения.",
        "en": "🏛 <b>{faculty_name}</b>\n\nThere are currently no active directions in this faculty.",
    },
    "select_direction_prompt": {
        "uz": "🏛 <b>Fakultet:</b> {faculty_name}\n\n⬇️ <i>O'zingiz tahsil olayotgan ta'lim yo'nalishini tanlang:</i>",
        "ru": "🏛 <b>Факультет:</b> {faculty_name}\n\n⬇️ <i>Выберите ваше направление обучения:</i>",
        "en": "🏛 <b>Faculty:</b> {faculty_name}\n\n⬇️ <i>Select your study direction:</i>",
    },
    "back_to_faculties": {
        "uz": "⬅️ Fakultetlar ro'yxatiga qaytish",
        "ru": "⬅️ Назад к факультетам",
        "en": "⬅️ Back to faculties",
    },
    "direction_not_found": {
        "uz": "Yo'nalish topilmadi!",
        "ru": "Направление не найдено!",
        "en": "Direction not found!",
    },
    "no_clubs": {
        "uz": "📚 <b>{direction_name}</b>\n\nUshbu yo'nalish bo'yicha hozircha faol to'garaklar mavjud emas.",
        "ru": "📚 <b>{direction_name}</b>\n\nПо этому направлению пока нет активных кружков.",
        "en": "📚 <b>{direction_name}</b>\n\nThere are currently no active clubs in this direction.",
    },
    "select_club_prompt": {
        "uz": "📚 <b>Yo'nalish:</b> {direction_name}\n\n⬇️ <i>Quyidagi to'garaklardan birini tanlang:</i>",
        "ru": "📚 <b>Направление:</b> {direction_name}\n\n⬇️ <i>Выберите один из кружков:</i>",
        "en": "📚 <b>Direction:</b> {direction_name}\n\n⬇️ <i>Select a club from below:</i>",
    },
    "back_to_directions": {
        "uz": "⬅️ Yo'nalishlar ro'yxatiga qaytish",
        "ru": "⬅️ Назад к направлениям",
        "en": "⬅️ Back to directions",
    },
    "club_not_found": {
        "uz": "To'garak topilmadi!",
        "ru": "Кружок не найден!",
        "en": "Club not found!",
    },
    "back_to_clubs": {
        "uz": "⬅️ To'garaklar ro'yxatiga qaytish",
        "ru": "⬅️ Назад к кружкам",
        "en": "⬅️ Back to clubs",
    },

    # 4. Club Details & Action Buttons
    "club_detail_card": {
        "uz": (
            "🎯 <b>To'garak:</b> {name}\n"
            "🏛 <b>Fakultet:</b> {faculty_name}\n"
            "📚 <b>Yo'nalish:</b> {direction_name}\n\n"
            "📝 <b>Tavsif:</b>\n{description}\n\n"
            "🗓 <b>Mashg'ulot kunlari:</b> {schedule_days}\n"
            "⏰ <b>Vaqti:</b> {schedule_time}\n"
            "📍 <b>Xonasi:</b> {room_location}\n"
            "👨‍🏫 <b>To'garak rahbari:</b> {leader_name} ({leader_contact})\n\n"
            "👥 <b>To'garak sig'imi:</b> {capacity_info}\n"
            "⏳ <b>Zaxira navbati:</b> {waiting_info}\n"
            "{deadline_info}"
        ),
        "ru": (
            "🎯 <b>Кружок:</b> {name}\n"
            "🏛 <b>Факультет:</b> {faculty_name}\n"
            "📚 <b>Направление:</b> {direction_name}\n\n"
            "📝 <b>Описание:</b>\n{description}\n\n"
            "🗓 <b>Дни занятий:</b> {schedule_days}\n"
            "⏰ <b>Время:</b> {schedule_time}\n"
            "📍 <b>Кабинет:</b> {room_location}\n"
            "👨‍🏫 <b>Руководитель:</b> {leader_name} ({leader_contact})\n\n"
            "👥 <b>Вместимость кружка:</b> {capacity_info}\n"
            "⏳ <b>Резервная очередь:</b> {waiting_info}\n"
            "{deadline_info}"
        ),
        "en": (
            "🎯 <b>Club:</b> {name}\n"
            "🏛 <b>Faculty:</b> {faculty_name}\n"
            "📚 <b>Direction:</b> {direction_name}\n\n"
            "📝 <b>Description:</b>\n{description}\n\n"
            "🗓 <b>Schedule Days:</b> {schedule_days}\n"
            "⏰ <b>Time:</b> {schedule_time}\n"
            "📍 <b>Room:</b> {room_location}\n"
            "👨‍🏫 <b>Club Leader:</b> {leader_name} ({leader_contact})\n\n"
            "👥 <b>Capacity:</b> {capacity_info}\n"
            "⏳ <b>Waiting List:</b> {waiting_info}\n"
            "{deadline_info}"
        ),
    },
    "btn_register": {
        "uz": "✍️ Ro'yxatdan o'tish",
        "ru": "✍️ Записаться",
        "en": "✍️ Register",
    },
    "btn_join_queue": {
        "uz": "⏳ Navbatga yozilish (Zaxira #{num})",
        "ru": "⏳ Встать в очередь (Резерв #{num})",
        "en": "⏳ Join waiting list (Queue #{num})",
    },
    "btn_deadline_expired": {
        "uz": "⛔ Ro'yxatdan o'tish yopilgan (Muddati tugagan)",
        "ru": "⛔ Регистрация закрыта (Срок истек)",
        "en": "⛔ Registration closed (Deadline passed)",
    },
    "deadline_alert": {
        "uz": "⚠️ Ushbu to'garakka ro'yxatdan o'tish muddati tugagan! Yangi arizalar qabul qilinmaydi.",
        "ru": "⚠️ Срок регистрации в этот кружок истек! Новые заявки не принимаются.",
        "en": "⚠️ Registration deadline for this club has expired! New applications are not accepted.",
    },
    "already_registered": {
        "uz": "⚠️ Siz allaqachon ushbu to'garakka a'zo bo'lgansiz!",
        "ru": "⚠️ Вы уже являетесь участником этого кружка!",
        "en": "⚠️ You are already registered for this club!",
    },
    "already_in_queue": {
        "uz": "⚠️ Siz allaqachon ushbu to'garak zaxira navbatidasiz{pos}!",
        "ru": "⚠️ Вы уже находитесь в очереди ожидания этого кружка{pos}!",
        "en": "⚠️ You are already in the waiting list for this club{pos}!",
    },

    # 5. Registration FSM Flow
    "reg_intro_active": {
        "uz": (
            "📝 <b>'{club}' to'garagiga ro'yxatdan o'tish</b>\n\n"
            "1/3. Iltimos, to'liq <b>ism-familiyangizni</b> kiriting:\n"
            "<i>(Masalan: Saidov Jasur Akmal o'g'li)</i>"
        ),
        "ru": (
            "📝 <b>Запись в кружок '{club}'</b>\n\n"
            "1/3. Пожалуйста, введите ваше полное <b>Ф.И.О.</b>:\n"
            "<i>(Например: Саидов Жасур Акмалович)</i>"
        ),
        "en": (
            "📝 <b>Registration for '{club}'</b>\n\n"
            "1/3. Please enter your <b>Full Name</b>:\n"
            "<i>(E.g.: Jasur Saidov)</i>"
        ),
    },
    "reg_intro_waiting": {
        "uz": (
            "📝 <b>'{club}' to'garagida asosiy o'rinlar to'lgan.</b>\n"
            "ℹ️ Siz <b>ZAXIRA (NAVBAT #{num})</b>ga yozilmoqdasiz.\n\n"
            "1/3. Iltimos, to'liq <b>ism-familiyangizni</b> kiriting:\n"
            "<i>(Masalan: Saidov Jasur Akmal o'g'li)</i>"
        ),
        "ru": (
            "📝 <b>В кружке '{club}' основные места заполнены.</b>\n"
            "ℹ️ Вы записываетесь в <b>РЕЗЕРВ (ОЧЕРЕДЬ #{num})</b>.\n\n"
            "1/3. Пожалуйста, введите ваше полное <b>Ф.И.О.</b>:\n"
            "<i>(Например: Саидов Жасур Акмалович)</i>"
        ),
        "en": (
            "📝 <b>Main spots are full for '{club}'.</b>\n"
            "ℹ️ You are joining the <b>WAITING LIST (QUEUE #{num})</b>.\n\n"
            "1/3. Please enter your <b>Full Name</b>:\n"
            "<i>(E.g.: Jasur Saidov)</i>"
        ),
    },
    "name_validation_err": {
        "uz": "⚠️ Iltimos, ism va familiyangizni to'liq kiriting!\n<i>(Kamida 2 ta so'z, masalan: Saidov Jasur)</i>",
        "ru": "⚠️ Пожалуйста, укажите имя и фамилию полностью!\n<i>(Минимум 2 слова, например: Саидов Жасур)</i>",
        "en": "⚠️ Please enter your full name!\n<i>(At least 2 words, e.g.: Jasur Saidov)</i>",
    },
    "select_course_prompt": {
        "uz": "Rahmat, <b>{full_name}</b>!\n\n2/3. Nechanchi kursda tahsil olasiz? Quyidagilardan tanlang:",
        "ru": "Спасибо, <b>{full_name}</b>!\n\n2/3. На каком курсе вы обучаетесь? Выберите ниже:",
        "en": "Thank you, <b>{full_name}</b>!\n\n2/3. Which academic year (course) are you in? Select below:",
    },
    "course_1": {"uz": "1-kurs", "ru": "1-й курс", "en": "1st year"},
    "course_2": {"uz": "2-kurs", "ru": "2-й курс", "en": "2nd year"},
    "course_3": {"uz": "3-kurs", "ru": "3-й курс", "en": "3rd year"},
    "course_4": {"uz": "4-kurs", "ru": "4-й курс", "en": "4th year"},
    "send_phone_prompt": {
        "uz": (
            "3/3. 📞 <b>Telefon raqamingizni yuboring:</b>\n\n"
            "Quyidagi <b>'Telefon raqamimni ulashish'</b> tugmasini bosing yoki "
            "qo'lda yozib yuboring (Masalan: <code>+998901234567</code>):"
        ),
        "ru": (
            "3/3. 📞 <b>Отправьте ваш номер телефона:</b>\n\n"
            "Нажмите кнопку <b>'Поделиться номером телефона'</b> ниже или "
            "введите вручную (Например: <code>+998901234567</code>):"
        ),
        "en": (
            "3/3. 📞 <b>Send your phone number:</b>\n\n"
            "Tap the <b>'Share my phone number'</b> button below or "
            "type it manually (e.g.: <code>+998901234567</code>):"
        ),
    },
    "phone_validation_err": {
        "uz": (
            "⚠️ Telefon raqam noto'g'ri kiritildi!\n"
            "Iltimos, pastdagi <b>'Telefon raqamimni ulashish'</b> tugmasidan foydalaning "
            "yoki raqamingizni <code>+998901234567</code> formatida yozing."
        ),
        "ru": (
            "⚠️ Неверный формат номера телефона!\n"
            "Пожалуйста, используйте кнопку <b>'Поделиться номером телефона'</b> ниже "
            "или введите номер в формате <code>+998901234567</code>."
        ),
        "en": (
            "⚠️ Invalid phone number format!\n"
            "Please use the <b>'Share my phone number'</b> button below "
            "or enter in <code>+998901234567</code> format."
        ),
    },
    "data_received": {
        "uz": "Ma'lumotlar qabul qilindi.",
        "ru": "Данные приняты.",
        "en": "Data received.",
    },
    "review_card": {
        "uz": (
            "📋 <b>Arizangiz ma'lumotlarini tekshiring:</b>\n\n"
            "👤 <b>F.I.Sh:</b> {full_name}\n"
            "🏛 <b>Fakultet:</b> {faculty_name}\n"
            "📚 <b>Ta'lim yo'nalishi:</b> {direction_name}\n"
            "🎯 <b>To'garak:</b> {club_name}\n"
            "🎓 <b>Kurs:</b> {course_level}-kurs\n"
            "📞 <b>Telefon:</b> {phone_number}\n"
            "💬 <b>Telegram:</b> {telegram_username}\n\n"
            "<i>Barcha ma'lumotlar to'g'rimi? Tasdiqlash uchun quyidagi tugmani bosing:</i>"
        ),
        "ru": (
            "📋 <b>Проверьте данные вашей заявки:</b>\n\n"
            "👤 <b>Ф.И.О.:</b> {full_name}\n"
            "🏛 <b>Факультет:</b> {faculty_name}\n"
            "📚 <b>Направление:</b> {direction_name}\n"
            "🎯 <b>Кружок:</b> {club_name}\n"
            "🎓 <b>Курс:</b> {course_level}-й курс\n"
            "📞 <b>Телефон:</b> {phone_number}\n"
            "💬 <b>Telegram:</b> {telegram_username}\n\n"
            "<i>Все данные верны? Нажмите кнопку ниже для подтверждения:</i>"
        ),
        "en": (
            "📋 <b>Review your registration details:</b>\n\n"
            "👤 <b>Full Name:</b> {full_name}\n"
            "🏛 <b>Faculty:</b> {faculty_name}\n"
            "📚 <b>Direction:</b> {direction_name}\n"
            "🎯 <b>Club:</b> {club_name}\n"
            "🎓 <b>Course:</b> {course_level} year\n"
            "📞 <b>Phone:</b> {phone_number}\n"
            "💬 <b>Telegram:</b> {telegram_username}\n\n"
            "<i>Are all details correct? Tap below to confirm:</i>"
        ),
    },
    "btn_confirm": {
        "uz": "✅ Ha, tasdiqlayman",
        "ru": "✅ Да, подтверждаю",
        "en": "✅ Yes, confirm",
    },
    "reg_cancelled": {
        "uz": "❌ Ro'yxatdan o'tish bekor qilindi.",
        "ru": "❌ Регистрация отменена.",
        "en": "❌ Registration cancelled.",
    },
    "reg_success_active": {
        "uz": (
            "🎉 <b>TABRIKLAYMIZ! RO'YXATDAN O'TISH MUVAFFAQIYATLI YAKUNLANDI!</b>\n\n"
            "Siz <b>'{club}'</b> to'garagining <b>asosiy a'zosi</b> bo'ldingiz.\n\n"
            "📌 <b>Eslatma:</b> To'garak rahbari yaqin vaqt ichida siz bilan bog'lanadi. "
            "Mashg'ulotlarga o'z vaqtida kelishingizni so'raymiz.\n\n"
            "<i>Yana boshqa to'garaklar bilan tanishish uchun /start ni bosing.</i>"
        ),
        "ru": (
            "🎉 <b>ПОЗДРАВЛЯЕМ! РЕГИСТРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!</b>\n\n"
            "Вы стали <b>основным участником</b> кружка <b>'{club}'</b>.\n\n"
            "📌 <b>Примечание:</b> Руководитель кружка свяжется с вами в ближайшее время. "
            "Просим приходить на занятия вовремя.\n\n"
            "<i>Чтобы посмотреть другие кружки, нажмите /start.</i>"
        ),
        "en": (
            "🎉 <b>CONGRATULATIONS! REGISTRATION COMPLETED SUCCESSFULLY!</b>\n\n"
            "You are now an <b>active member</b> of the <b>'{club}'</b> club.\n\n"
            "📌 <b>Note:</b> The club leader will contact you soon. "
            "Please attend the sessions on time.\n\n"
            "<i>To explore more clubs, press /start.</i>"
        ),
    },
    "reg_success_waiting": {
        "uz": (
            "📋 <b>SIZ ZAXIRA (NAVBAT) RO'YXATIGA YOZILDINGIZ!</b>\n\n"
            "🎯 <b>To'garak:</b> {club}\n"
            "🔢 <b>Sizning navbat raqamingiz:</b> <b>#{num}</b>\n\n"
            "📌 <b>Qanday ishlaydi?</b>\n"
            "Ushbu to'garakda asosiy o'rinlar to'lganligi sababli siz zaxira navbatidasiz. "
            "Agar biror faol talaba to'garakdan chiqsa yoki a'zoligini bekor qilsa, "
            "navbat bo'yicha <b>avtomatik tarzda asosiy a'zolar ro'yxatiga o'tkazilasiz</b> va bot sizga darhol xushxabar yuboradi!\n\n"
            "<i>O'z to'garaklaringiz va navbat holatini <b>'📋 Mening to'garaklarim'</b> bo'limida kuzatib borishingiz mumkin.</i>"
        ),
        "ru": (
            "📋 <b>ВЫ ЗАПИСАНЫ В РЕЗЕРВНЫЙ СПИСОК (ОЧЕРЕДЬ)!</b>\n\n"
            "🎯 <b>Кружок:</b> {club}\n"
            "🔢 <b>Ваш номер в очереди:</b> <b>#{num}</b>\n\n"
            "📌 <b>Как это работает?</b>\n"
            "Поскольку основные места заполнены, вы находитесь в резерве. "
            "Если какой-либо участник покинет кружок, вы <b>автоматически перейдете в основной состав</b>, "
            "и бот сразу отправит вам уведомление!\n\n"
            "<i>Вы можете следить за статусом в разделе <b>'📋 Мои кружки'</b>.</i>"
        ),
        "en": (
            "📋 <b>YOU HAVE BEEN ADDED TO THE WAITING LIST (QUEUE)!</b>\n\n"
            "🎯 <b>Club:</b> {club}\n"
            "🔢 <b>Your queue position:</b> <b>#{num}</b>\n\n"
            "📌 <b>How it works:</b>\n"
            "Because regular seats are full, you are on the waiting list. "
            "If an active member leaves, you will be <b>automatically promoted to the active members list</b>, "
            "and the bot will notify you instantly!\n\n"
            "<i>You can track your status in <b>'📋 My clubs'</b>.</i>"
        ),
    },

    # 6. My Clubs
    "my_clubs_empty": {
        "uz": (
            "📋 <b>Siz hozircha hech qaysi to'garakka a'zo emassiz va navbatda yo'qsiz.</b>\n\n"
            "To'garaklar bilan tanishish va a'zo bo'lish uchun pastdagi "
            "<b>'🏛 To'garaklar katalogi'</b> tugmasini bosing."
        ),
        "ru": (
            "📋 <b>Вы пока не состоите ни в одном кружке и не находитесь в очереди.</b>\n\n"
            "Чтобы ознакомиться с кружками и записаться, нажмите "
            "<b>'🏛 Каталог кружков'</b> ниже."
        ),
        "en": (
            "📋 <b>You are not enrolled in any clubs and not in any waiting list.</b>\n\n"
            "To browse clubs and enroll, tap "
            "<b>'🏛 Clubs catalog'</b> below."
        ),
    },
    "my_active_title": {
        "uz": "✅ <b>Siz asosiy a'zo bo'lgan to'garaklar ({count} ta):</b>",
        "ru": "✅ <b>Кружки, в которых вы являетесь основным участником ({count}):</b>",
        "en": "✅ <b>Clubs you are an active member of ({count}):</b>",
    },
    "my_waiting_title": {
        "uz": "⏳ <b>Siz zaxira navbatida turgan to'garaklar ({count} ta):</b>",
        "ru": "⏳ <b>Кружки, в которых вы находитесь в резерве ({count}):</b>",
        "en": "⏳ <b>Clubs you are waiting in queue for ({count}):</b>",
    },
    "btn_leave_club": {
        "uz": "❌ To'garakdan chiqish",
        "ru": "❌ Выйти из кружка",
        "en": "❌ Leave club",
    },
    "btn_leave_queue": {
        "uz": "❌ Navbatdan chiqish",
        "ru": "❌ Покинуть очередь",
        "en": "❌ Leave waiting list",
    },
    "ask_leave_prompt": {
        "uz": (
            "⚠️ <b>Haqiqatdan ham '{club_name}' to'garagining {status_name} chiqmoqchimisiz?</b>\n\n"
            "<i>Agar chiqsangiz, bo'shagan o'rin navbatdagi talabaga avtomatik tarzda beriladi.</i>"
        ),
        "ru": (
            "⚠️ <b>Вы уверены, что хотите выйти из {status_name} кружка '{club_name}'?</b>\n\n"
            "<i>Если вы выйдете, освободившееся место автоматически перейдет следующему студенту в очереди.</i>"
        ),
        "en": (
            "⚠️ <b>Are you sure you want to leave the {status_name} of '{club_name}'?</b>\n\n"
            "<i>If you leave, the freed spot will be automatically assigned to the next student in queue.</i>"
        ),
    },
    "status_active_gen": {
        "uz": "asosiy a'zoligidan",
        "ru": "основного состава",
        "en": "active membership",
    },
    "status_waiting_gen": {
        "uz": "zaxira navbatidan",
        "ru": "очереди ожидания",
        "en": "waiting list",
    },
    "btn_confirm_leave": {
        "uz": "✅ Ha, to'garakdan chiqish",
        "ru": "✅ Да, покинуть",
        "en": "✅ Yes, leave",
    },
    "leave_cancelled": {
        "uz": "✅ Amaliyot bekor qilindi. A'zoligingiz saqlab qolindi.",
        "ru": "✅ Операция отменена. Ваше членство сохранено.",
        "en": "✅ Action cancelled. Your membership was preserved.",
    },
    "leave_success": {
        "uz": "✅ Siz to'garakdan (navbatdan) muvaffaqiyatli chiqdingiz.",
        "ru": "✅ Вы успешно вышли из кружка (очереди).",
        "en": "✅ You successfully left the club (waiting list).",
    },

    # 7. Promotion Notification (Sent automatically to promoted student)
    "promotion_notification": {
        "uz": (
            "🎉 <b>AJOYIB YANGILIK! TO'GARAKDA BO'SH O'RIN PAYDO BO'LDI!</b>\n\n"
            "Hurmatli <b>{full_name}</b>!\n\n"
            "Siz navbatda turgan <b>'{club_name}'</b> to'garagida bo'sh o'rin ochildi va siz avtomatik tarzda "
            "<b>ASOSIY A'ZOLAR RO'YXATIGA QABUL QILINDINGIZ!</b> ✅\n\n"
            "🏛 <b>Fakultet:</b> {faculty_name}\n"
            "📚 <b>Yo'nalish:</b> {direction_name}\n"
            "🗓 <b>Mashg'ulot kunlari:</b> {schedule_days}\n"
            "⏰ <b>Vaqti:</b> {schedule_time}\n"
            "📍 <b>Xonasi:</b> {room_location}\n"
            "👨‍🏫 <b>To'garak rahbari:</b> {leader_name} ({leader_contact})\n\n"
            "<i>Mashg'ulotlarga o'z vaqtida qatnashishingizni so'raymiz!</i>"
        ),
        "ru": (
            "🎉 <b>ОТЛИЧНАЯ НОВОСТЬ! В КРУЖКЕ ОСВОБОДИЛОСЬ МЕСТО!</b>\n\n"
            "Уважаемый(ая) <b>{full_name}</b>!\n\n"
            "В кружке <b>'{club_name}'</b>, в котором вы ожидали очередь, появилось свободное место, и вы "
            "<b>АВТОМАТИЧЕСКИ ЗАЧИСЛЕНЫ В ОСНОВНОЙ СОСТАВ!</b> ✅\n\n"
            "🏛 <b>Факультет:</b> {faculty_name}\n"
            "📚 <b>Направление:</b> {direction_name}\n"
            "🗓 <b>Дни занятий:</b> {schedule_days}\n"
            "⏰ <b>Время:</b> {schedule_time}\n"
            "📍 <b>Кабинет:</b> {room_location}\n"
            "👨‍🏫 <b>Руководитель:</b> {leader_name} ({leader_contact})\n\n"
            "<i>Просим посещать занятия своевременно!</i>"
        ),
        "en": (
            "🎉 <b>EXCELLENT NEWS! A SPOT OPENED UP IN THE CLUB!</b>\n\n"
            "Dear <b>{full_name}</b>!\n\n"
            "A spot has opened up in <b>'{club_name}'</b> that you were waiting for, and you have been "
            "<b>AUTOMATICALLY PROMOTED TO ACTIVE MEMBERSHIP!</b> ✅\n\n"
            "🏛 <b>Faculty:</b> {faculty_name}\n"
            "📚 <b>Direction:</b> {direction_name}\n"
            "🗓 <b>Schedule Days:</b> {schedule_days}\n"
            "⏰ <b>Time:</b> {schedule_time}\n"
            "📍 <b>Room:</b> {room_location}\n"
            "👨‍🏫 <b>Club Leader:</b> {leader_name} ({leader_contact})\n\n"
            "<i>Please make sure to attend sessions on time!</i>"
        ),
    },

    # 8. About & Misc
    "about_text": {
        "uz": (
            "ℹ️ <b>Universitet Iqtidorli Talabalar Tizimi</b>\n\n"
            "Bu platforma universitetimizdagi iqtidorli talabalarning ilmiy, ijodiy va amaliy "
            "salohiyatini rivojlantirishga mo'ljallangan.\n\n"
            "📌 <b>Bot imkoniyatlari:</b>\n"
            "• Fakultet va yo'nalishlar kesimida to'garaklarni qidirish\n"
            "• To'garaklar sig'imi va qabul muddatlarini ko'rish\n"
            "• Asosiy o'rinlar to'lganda avtomatik navbatga yozilish\n"
            "• Bo'shagan o'rinlarga navbatdagi talabalarning avtomatik qabul qilinishi va xabardor qilinishi\n"
            "• 'Mening to'garaklarim' bo'limi orqali shaxsiy a'zoliklarni va navbatni boshqarish\n"
            "• 3 ta tilda (O'zbek, Rus, Ingliz) to'liq ishlash\n\n"
            "To'garaklar katalogiga o'tish uchun quyidagi tugmani bosing."
        ),
        "ru": (
            "ℹ️ <b>Система Одаренных Студентов Университета</b>\n\n"
            "Эта платформа предназначена для поддержки и развития научного, творческого "
            "и практического потенциала одаренных студентов нашего университета.\n\n"
            "📌 <b>Возможности бота:</b>\n"
            "• Поиск кружков по факультетам и направлениям\n"
            "• Просмотр лимита мест и сроков регистрации\n"
            "• Автоматическая запись в очередь ожидания при заполнении мест\n"
            "• Автоматическое продвижение из очереди и мгновенное уведомление при освобождении места\n"
            "• Управление членством и очередью в разделе 'Мои кружки'\n"
            "• Полная поддержка 3-х языков (Узбекский, Русский, Английский)\n\n"
            "Для перехода к каталогу кружков нажмите кнопку ниже."
        ),
        "en": (
            "ℹ️ <b>University Gifted Students System</b>\n\n"
            "This platform is designed to nurture the academic, creative, and practical "
            "talents of gifted students across our university.\n\n"
            "📌 <b>Bot Features:</b>\n"
            "• Browse clubs by faculty and study directions\n"
            "• View group capacity limits and registration deadlines\n"
            "• Automatic waiting queue placement when clubs reach capacity\n"
            "• Auto-promotion and instant notification when spots open up\n"
            "• Self-management of enrollments and queue positions via 'My clubs'\n"
            "• Full multi-language support (Uzbek, Russian, English)\n\n"
            "Press the button below to open the clubs catalog."
        ),
    },
    "no_active_process": {
        "uz": "Hech qanday faol jarayon yo'q.",
        "ru": "Нет активных процессов.",
        "en": "There is no active process.",
    },
    "cancel_done": {
        "uz": "❌ Amaliyot bekor qilindi. Bosh sahifaga qaytish uchun /start ni bosing.",
        "ru": "❌ Действие отменено. Нажмите /start для возврата в главное меню.",
        "en": "❌ Action cancelled. Press /start to return to the main menu.",
    },
}


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """Retrieve localized message string formatted with kwargs."""
    lang = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
    template_dict = MESSAGES.get(key, {})
    template = template_dict.get(lang) or template_dict.get(DEFAULT_LANGUAGE, key)
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def get_lang_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline buttons to choose language: UZ, RU, EN."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="set_lang:uz")
    builder.button(text="🇷🇺 Русский", callback_data="set_lang:ru")
    builder.button(text="🇬🇧 English", callback_data="set_lang:en")
    builder.adjust(1)
    return builder.as_markup()


async def get_user_lang(
    telegram_id: int,
    session: Optional[AsyncSession] = None,
    state: Optional[FSMContext] = None
) -> str:
    """
    Resolve preferred language for a user:
    1. Check FSM state data
    2. Check Database (Student model)
    3. Fallback to DEFAULT_LANGUAGE ('uz')
    """
    if state:
        data = await state.get_data()
        if data.get("user_lang") in LANGUAGES:
            return data["user_lang"]

    if session:
        from src.repositories.student_repo import StudentRepository
        student_repo = StudentRepository(session)
        lang = await student_repo.get_language(telegram_id)
        if lang in LANGUAGES:
            return lang

    return DEFAULT_LANGUAGE
