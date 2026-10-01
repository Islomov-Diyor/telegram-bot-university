// Internationalization (i18n) for University Gifted Students Web Panel
// Languages: uz (Primary), ru, en

const I18N_LANGUAGES = ['uz', 'ru', 'en'];
const DEFAULT_LANG = 'uz';

const I18N_TRANSLATIONS = {
  uz: {
    // Brand & Sidebar
    "brand_title": "IQTIDORLI TALABALAR",
    "brand_subtitle": "Universitet Boshqaruv Tizimi",
    "nav_dashboard": "Dashboard",
    "nav_clubs": "To'garaklar",
    "nav_students": "Iqtidorli Talabalar",
    "nav_academic": "Fakultet va Yo'nalishlar",
    "nav_settings": "Sozlamalar & Notification",
    "logout": "Chiqish",

    // Dashboard
    "dash_title": "Universitet Ko'rsatkichlari",
    "dash_desc": "Iqtidorli talabalar va to'garaklar faoliyatining umumiy statistikasi",
    "refresh": "Yangilash",
    "kpi_students": "Asosiy A'zo Talabalar",
    "kpi_waiting": "Zaxira (Navbatda)",
    "kpi_clubs": "Faol To'garaklar",
    "kpi_faculties": "Fakultetlar",
    "kpi_directions": "Ta'lim Yo'nalishlari",
    "faculty_distribution": "Fakultetlar bo'yicha taqsimot",
    "top_clubs_fill": "To'garaklarning to'lganlik darajasi (Top 6)",
    "recent_students_title": "Oxirgi qabul qilingan talabalar",
    "recent_students_desc": "So'nggi ro'yxatdan o'tgan yoki navbatga yozilgan talabalar",
    "no_recent_students": "Hozircha ro'yxatdan o'tgan talabalar yo'q.",
    "no_members_yet": "Hozircha a'zo bo'lgan talabalar yo'q.",
    "no_data": "Ma'lumotlar mavjud emas.",
    "students_count_suffix": "nafar talaba",
    "people_suffix": "nafar",

    // Table Headers
    "th_num": "№",
    "th_student_name": "Talaba F.I.Sh",
    "th_club": "To'garak",
    "th_faculty": "Fakultet",
    "th_direction": "Ta'lim Yo'nalishi",
    "th_faculty_direction": "Fakultet va Yo'nalish",
    "th_course": "Kurs",
    "th_status": "Holati",
    "th_phone": "Telefon raqam",
    "th_telegram": "Telegram",
    "th_reg_date": "Ro'yxatdan o'tgan",
    "th_actions": "Amallar",
    "th_leader": "Rahbar va Aloqa",
    "th_schedule": "Mashg'ulot vaqti",
    "th_capacity": "Sig'im va Navbat",
    "th_deadline": "Qabul muddati",
    "th_code": "Kodi",
    "th_directions_count": "Yo'nalishlar soni",
    "th_clubs_count": "To'garaklar soni",

    // Badges & Statuses
    "status_active": "✅ Asosiy a'zo",
    "status_waiting": "⏳ Navbatda (#{pos})",
    "status_full": "🔒 To'lgan ({cur}/{max} nafar | Navbatda: {wait})",
    "status_spots": "👥 {cur}/{max} nafar a'zo",
    "status_unlimited": "👥 {cur} nafar a'zo",
    "status_deadline_passed": "⛔ Muddat tugagan ({date})",
    "status_deadline_open": "⏳ Muddat: {date}",

    // Clubs Tab
    "clubs_title": "To'garaklar Boshqaruvi",
    "clubs_desc": "Universitetdagi barcha ilmiy va ijodiy to'garaklar ro'yxati, sig'imi va muddatlari",
    "btn_add_club": "Yangi to'garak qo'shish",
    "btn_export": "Eksport qilish",
    "export_excel": "📊 Excel (.xlsx)",
    "export_csv": "📄 CSV (.csv)",
    "filter_all_faculties": "Barcha fakultetlar",
    "filter_select_faculty": "Fakultetni tanlang",
    "filter_select_direction": "Yo'nalishni tanlang",
    "filter_all_clubs": "Barcha to'garaklar",
    "no_clubs_found": "To'garaklar topilmadi.",
    "edit": "Tahrirlash",
    "delete": "O'chirish",
    "cancel_reg": "Bekor qilish",
    "clubs_count_suffix": "{count} ta to'garak",

    // Students Tab
    "students_title": "Iqtidorli Talabalar Ro'yxati",
    "students_desc": "To'garaklarga a'zo bo'lgan yoki navbatda turgan barcha talabalar bazasi",
    "search_student_placeholder": "F.I.Sh yoki telefon bo'yicha qidirish...",
    "filter_all_courses": "Barcha kurslar",
    "filter_course_1": "1-kurs",
    "filter_course_2": "2-kurs",
    "filter_course_3": "3-kurs",
    "filter_course_4": "4-kurs",
    "filter_all_statuses": "Barcha holatlar",
    "filter_status_active": "Asosiy a'zolar",
    "filter_status_waiting": "Zaxira navbatidagilar",
    "no_students_found": "A'zo bo'lgan yoki navbatdagi talabalar topilmadi.",

    // Academic Tab
    "academic_title": "Fakultet va Yo'nalishlar",
    "academic_desc": "Universitet ta'lim tuzilmasi va ixtisosliklar boshqaruvi",
    "btn_add_faculty": "Fakultet qo'shish",
    "btn_add_direction": "Yo'nalish qo'shish",
    "faculties_table_title": "Fakultetlar Ro'yxati",
    "directions_table_title": "Ta'lim Yo'nalishlari Ro'yxati",
    "directions_count_badge": "{count} ta yo'nalish",

    // Settings Tab
    "settings_title": "Tizim Sozlamalari & Bildirishnomalar",
    "settings_desc": "Telegram kanal integratsiyasi va administrator xavfsizlik sozlamalari",
    "telegram_mgmt_card": "Telegram Boshqaruv Kanali",
    "telegram_mgmt_desc": "Talabalar to'garakka ro'yxatdan o'tganda yangi arizalar avtomatik ravishda ushbu kanalga yuboriladi.",
    "channel_id_label": "Kanal Username yoki ID (Masalan: @universitet_iqtidorli yoki -1001234567890)",
    "btn_test_ping": "🔔 Sinov xabari yuborish",
    "btn_save": "Saqlash",
    "admin_personal_tg": "Shaxsiy Telegram Bildirishnoma",
    "admin_personal_desc": "O'z shaxsiy Telegram ID raqamingizni kiritsangiz, bot sizga ham arizalarni yuboradi.",
    "your_tg_id": "Sizning Telegram Chat ID",
    "security_card": "Xavfsizlik & Parolni Yangilash",
    "security_desc": "Administrator hisobining kirish parolini o'zgartirish.",
    "current_password": "Hozirgi parol",
    "new_password": "Yangi parol (kamida 8 ta belgi)",
    "confirm_password": "Yangi parolni tasdiqlang",
    "btn_update_password": "Parolni yangilash",
    "tg_guide_title": "Telegram Bot Tezkor Yo'riqnoma",
    "tg_step_1": "1. Botni Telegramda oching:",
    "tg_step_2": "2. Kanalga botni administrator qilib qo'shing va post yozish huquqini bering.",
    "tg_step_3": "3. Kanal username (@kanal_nomi) yoki ID raqamini chapdagi maydonga kiriting va 'Saqlash' tugmasini bosing.",
    "tg_step_4": "4. 'Sinov xabari yuborish' tugmasini bosib bot ishlashini tekshirib ko'ring.",

    // Modals
    "modal_add_club": "Yangi to'garak ochish",
    "modal_edit_club": "To'garakni tahrirlash",
    "form_club_direction": "Ta'lim Yo'nalishi *",
    "form_club_name": "To'garak Nomi *",
    "form_club_name_placeholder": "Masalan: Yosh Dasturchilar To'garagi",
    "form_club_desc": "To'garak Tavsifi",
    "form_club_desc_placeholder": "To'garak maqsadi va vazifalari haqida...",
    "form_club_days": "Mashg'ulot Kunlari *",
    "form_club_days_placeholder": "Masalan: Seshanba, Payshanba",
    "form_club_time": "Mashg'ulot Vaqti *",
    "form_club_time_placeholder": "Masalan: 14:00 - 16:00",
    "form_club_room": "Xona / Manzil *",
    "form_club_room_placeholder": "Masalan: 402-xona, B-bino",
    "form_club_leader": "To'garak Rahbari F.I.Sh *",
    "form_club_leader_placeholder": "Masalan: Dotsent Aliyev B. A.",
    "form_club_contact": "Rahbar Aloqa Ma'lumoti *",
    "form_club_contact_placeholder": "Masalan: +998901234567 yoki @aliyev_leader",
    "form_club_max_cap": "Maksimal Talabalar Sig'imi (Kvota)",
    "form_club_max_cap_hint": "0 kiritilsa sig'im cheklanmagan bo'ladi. Kvota to'lsa keyingi talabalar avtomatik navbatga yoziladi.",
    "form_club_deadline": "Ro'yxatdan o'tishning oxirgi muddati (Deadline)",
    "form_club_deadline_hint": "Agar muddat belgilansa, shu vaqtdan keyin yangi a'zolar va navbat qabul qilish yopiladi.",
    "btn_cancel_modal": "Bekor qilish",
    "btn_save_modal": "Saqlash",

    "modal_add_faculty": "Fakultet qo'shish",
    "modal_edit_faculty": "Fakultetni tahrirlash",
    "form_faculty_name": "Fakultet Nomi *",
    "form_faculty_name_placeholder": "Masalan: Xorijiy Tillar Fakulteti",
    "form_faculty_code": "Fakultet Qisqa Kodi",
    "form_faculty_code_placeholder": "Masalan: XTF",

    "modal_add_direction": "Yo'nalish qo'shish",
    "modal_edit_direction": "Yo'nalishni tahrirlash",
    "form_direction_faculty": "Tegishli Fakultet *",
    "form_direction_name": "Yo'nalish Nomi *",
    "form_direction_name_placeholder": "Masalan: Ingliz Tili va Adabiyoti",
    "form_direction_code": "Yo'nalish Kodi",
    "form_direction_code_placeholder": "Masalan: 60111800",

    // Confirmations & Toasts
    "confirm_delete_club": "Haqiqatdan ham ushbu to'garakni o'chirmoqchimisiz? Undagi talabalar a'zoligi ham bekor qilinadi.",
    "confirm_delete_faculty": "Fakultetni o'chirmoqchimisiz? Unga tegishli yo'nalishlar va to'garaklar ham o'chiriladi.",
    "confirm_delete_direction": "Yo'nalishni o'chirmoqchimisiz?",
    "confirm_cancel_reg": "Ushbu talabaning to'garakka a'zoligini bekor qilmoqchimisiz? Agar navbatda talaba bo'lsa, u avtomatik asosiy a'zolikka qabul qilinadi va unga bot orqali xabar yuboriladi.",
    "toast_data_refreshed": "Ma'lumotlar muvaffaqiyatli yangilandi!",
    "toast_refresh_error": "Yangilashda xatolik yuz berdi",
    "toast_club_saved": "To'garak ma'lumotlari yangilandi",
    "toast_club_created": "Yangi to'garak yaratildi",
    "toast_club_deleted": "To'garak muvaffaqiyatli o'chirildi",
    "toast_faculty_saved": "Fakultet saqlandi",
    "toast_faculty_deleted": "Fakultet o'chirildi",
    "toast_direction_saved": "Yo'nalish saqlandi",
    "toast_direction_deleted": "Yo'nalish o'chirildi",
    "toast_channel_saved": "Boshqaruv kanali muvaffaqiyatli saqlandi!",
    "toast_chat_id_saved": "Telegram Chat ID muvaffaqiyatli saqlandi!",
    "toast_password_changed": "Parol muvaffaqiyatli o'zgartirildi!",
    "toast_password_mismatch": "Yangi parollar bir-biriga mos kelmadi!",
    "toast_password_min_len": "Yangi parol kamida 8 ta belgidan iborat bo'lishi kerak!",

    // Login Page
    "login_page_title": "Kirish | Universitet Iqtidorli Talabalar Tizimi",
    "login_brand_title": "Iqtidorli Talabalar Tizimi",
    "login_brand_subtitle": "Universitet Administrator Paneli",
    "login_username_label": "Administrator Logini",
    "login_password_label": "Maxfiy Parol",
    "login_submit_btn": "Tizimga kirish",
    "login_error_invalid": "Login yoki parol noto'g'ri!",
    "login_error_generic": "Kirishda xatolik yuz berdi",
    "logging_in": "Kirilmoqda..."
  },

  ru: {
    // Brand & Sidebar
    "brand_title": "ОДАРЕННЫЕ СТУДЕНТЫ",
    "brand_subtitle": "Система управления университетом",
    "nav_dashboard": "Панель управления",
    "nav_clubs": "Кружки",
    "nav_students": "Одаренные студенты",
    "nav_academic": "Факультеты и направления",
    "nav_settings": "Настройки и уведомления",
    "logout": "Выйти",

    // Dashboard
    "dash_title": "Показатели университета",
    "dash_desc": "Общая статистика одаренных студентов и деятельности кружков",
    "refresh": "Обновить",
    "kpi_students": "Основные участники",
    "kpi_waiting": "В резерве (Очередь)",
    "kpi_clubs": "Активные кружки",
    "kpi_faculties": "Факультеты",
    "kpi_directions": "Направления обучения",
    "faculty_distribution": "Распределение по факультетам",
    "top_clubs_fill": "Заполняемость кружков (Топ 6)",
    "recent_students_title": "Недавно принятые студенты",
    "recent_students_desc": "Последние зарегистрированные или записанные в очередь студенты",
    "no_recent_students": "Пока нет зарегистрированных студентов.",
    "no_members_yet": "Пока нет участников.",
    "no_data": "Данные отсутствуют.",
    "students_count_suffix": "студентов",
    "people_suffix": "чел.",

    // Table Headers
    "th_num": "№",
    "th_student_name": "Ф.И.О. студента",
    "th_club": "Кружок",
    "th_faculty": "Факультет",
    "th_direction": "Направление",
    "th_faculty_direction": "Факультет и направление",
    "th_course": "Курс",
    "th_status": "Статус",
    "th_phone": "Телефон",
    "th_telegram": "Telegram",
    "th_reg_date": "Дата регистрации",
    "th_actions": "Действия",
    "th_leader": "Руководитель и контакты",
    "th_schedule": "Время занятий",
    "th_capacity": "Вместимость и очередь",
    "th_deadline": "Срок приема",
    "th_code": "Код",
    "th_directions_count": "Количество направлений",
    "th_clubs_count": "Количество кружков",

    // Badges & Statuses
    "status_active": "✅ Основной участник",
    "status_waiting": "⏳ В очереди (#{pos})",
    "status_full": "🔒 Заполнен ({cur}/{max} чел. | В очереди: {wait})",
    "status_spots": "👥 {cur}/{max} участников",
    "status_unlimited": "👥 {cur} участников",
    "status_deadline_passed": "⛔ Срок истек ({date})",
    "status_deadline_open": "⏳ Срок: {date}",

    // Clubs Tab
    "clubs_title": "Управление кружками",
    "clubs_desc": "Список, вместимость и сроки всех научных и творческих кружков университета",
    "btn_add_club": "Добавить кружок",
    "btn_export": "Экспорт",
    "export_excel": "📊 Excel (.xlsx)",
    "export_csv": "📄 CSV (.csv)",
    "filter_all_faculties": "Все факультеты",
    "filter_select_faculty": "Выберите факультет",
    "filter_select_direction": "Выберите направление",
    "filter_all_clubs": "Все кружки",
    "no_clubs_found": "Кружки не найдены.",
    "edit": "Редактировать",
    "delete": "Удалить",
    "cancel_reg": "Отменить",
    "clubs_count_suffix": "{count} кружков",

    // Students Tab
    "students_title": "Список одаренных студентов",
    "students_desc": "База всех студентов, записанных в кружки или находящихся в очереди",
    "search_student_placeholder": "Поиск по Ф.И.О. или телефону...",
    "filter_all_courses": "Все курсы",
    "filter_course_1": "1-й курс",
    "filter_course_2": "2-й курс",
    "filter_course_3": "3-й курс",
    "filter_course_4": "4-й курс",
    "filter_all_statuses": "Все статусы",
    "filter_status_active": "Основные участники",
    "filter_status_waiting": "В резервной очереди",
    "no_students_found": "Студенты не найдены.",

    // Academic Tab
    "academic_title": "Факультеты и направления",
    "academic_desc": "Управление структурой обучения и специальностями университета",
    "btn_add_faculty": "Добавить факультет",
    "btn_add_direction": "Добавить направление",
    "faculties_table_title": "Список факультетов",
    "directions_table_title": "Список направлений обучения",
    "directions_count_badge": "{count} направлений",

    // Settings Tab
    "settings_title": "Настройки системы & Уведомления",
    "settings_desc": "Интеграция с Telegram-каналом и параметры безопасности администратора",
    "telegram_mgmt_card": "Канал управления Telegram",
    "telegram_mgmt_desc": "Когда студенты регистрируются в кружок, новые заявки автоматически отправляются в этот канал.",
    "channel_id_label": "Username или ID канала (Например: @universitet_iqtidorli или -1001234567890)",
    "btn_test_ping": "🔔 Отправить тестовое сообщение",
    "btn_save": "Сохранить",
    "admin_personal_tg": "Личные уведомления Telegram",
    "admin_personal_desc": "Укажите ваш личный Telegram ID, чтобы бот также отправлял заявки вам.",
    "your_tg_id": "Ваш Telegram Chat ID",
    "security_card": "Безопасность & Смена пароля",
    "security_desc": "Изменение пароля учетной записи администратора.",
    "current_password": "Текущий пароль",
    "new_password": "Новый пароль (минимум 8 символов)",
    "confirm_password": "Подтвердите новый пароль",
    "btn_update_password": "Обновить пароль",
    "tg_guide_title": "Краткая инструкция по Telegram-боту",
    "tg_step_1": "1. Откройте бота в Telegram:",
    "tg_step_2": "2. Добавьте бота администратором в ваш канал с правом публикации сообщений.",
    "tg_step_3": "3. Введите username (@название_канала) или ID канала в поле слева и нажмите 'Сохранить'.",
    "tg_step_4": "4. Нажмите кнопку 'Отправить тестовое сообщение' для проверки связи.",

    // Modals
    "modal_add_club": "Создать кружок",
    "modal_edit_club": "Редактировать кружок",
    "form_club_direction": "Направление обучения *",
    "form_club_name": "Название кружка *",
    "form_club_name_placeholder": "Например: Кружок юных программистов",
    "form_club_desc": "Описание кружка",
    "form_club_desc_placeholder": "О целях и задачах кружка...",
    "form_club_days": "Дни занятий *",
    "form_club_days_placeholder": "Например: Вторник, Четверг",
    "form_club_time": "Время занятий *",
    "form_club_time_placeholder": "Например: 14:00 - 16:00",
    "form_club_room": "Кабинет / Адрес *",
    "form_club_room_placeholder": "Например: Аудитория 402, Корпус Б",
    "form_club_leader": "Ф.И.О. руководителя *",
    "form_club_leader_placeholder": "Например: Доцент Алиев Б. А.",
    "form_club_contact": "Контакты руководителя *",
    "form_club_contact_placeholder": "Например: +998901234567 или @aliyev_leader",
    "form_club_max_cap": "Лимит мест (Квота)",
    "form_club_max_cap_hint": "При значении 0 лимит отсутствует. При заполнении квоты новые студенты встают в очередь.",
    "form_club_deadline": "Срок окончания регистрации (Дедлайн)",
    "form_club_deadline_hint": "После наступления дедлайна регистрация и запись в очередь автоматически закрываются.",
    "btn_cancel_modal": "Отмена",
    "btn_save_modal": "Сохранить",

    "modal_add_faculty": "Добавить факультет",
    "modal_edit_faculty": "Редактировать факультет",
    "form_faculty_name": "Название факультета *",
    "form_faculty_name_placeholder": "Например: Факультет иностранных языков",
    "form_faculty_code": "Код факультета",
    "form_faculty_code_placeholder": "Например: ФИЯ",

    "modal_add_direction": "Добавить направление",
    "modal_edit_direction": "Редактировать направление",
    "form_direction_faculty": "Факультет *",
    "form_direction_name": "Название направления *",
    "form_direction_name_placeholder": "Например: Английский язык и литература",
    "form_direction_code": "Код направления",
    "form_direction_code_placeholder": "Например: 60111800",

    // Confirmations & Toasts
    "confirm_delete_club": "Вы действительно хотите удалить этот кружок? Записи студентов также будут аннулированы.",
    "confirm_delete_faculty": "Удалить факультет? Связанные с ним направления и кружки также будут удалены.",
    "confirm_delete_direction": "Удалить направление?",
    "confirm_cancel_reg": "Отменить участие этого студента? Если в очереди есть студент, он автоматически будет зачислен в основной состав с уведомлением через бота.",
    "toast_data_refreshed": "Данные успешно обновлены!",
    "toast_refresh_error": "Ошибка при обновлении",
    "toast_club_saved": "Данные кружка обновлены",
    "toast_club_created": "Новый кружок создан",
    "toast_club_deleted": "Кружок успешно удален",
    "toast_faculty_saved": "Факультет сохранен",
    "toast_faculty_deleted": "Факультет удален",
    "toast_direction_saved": "Направление сохранено",
    "toast_direction_deleted": "Направление удалено",
    "toast_channel_saved": "Канал управления успешно сохранен!",
    "toast_chat_id_saved": "Telegram Chat ID успешно сохранен!",
    "toast_password_changed": "Пароль успешно изменен!",
    "toast_password_mismatch": "Новые пароли не совпадают!",
    "toast_password_min_len": "Новый пароль должен содержать не менее 8 символов!",

    // Login Page
    "login_page_title": "Вход | Система одаренных студентов университета",
    "login_brand_title": "Система одаренных студентов",
    "login_brand_subtitle": "Панель администратора университета",
    "login_username_label": "Логин администратора",
    "login_password_label": "Пароль",
    "login_submit_btn": "Войти в систему",
    "login_error_invalid": "Неверный логин или пароль!",
    "login_error_generic": "Ошибка при входе",
    "logging_in": "Вход..."
  },

  en: {
    // Brand & Sidebar
    "brand_title": "GIFTED STUDENTS",
    "brand_subtitle": "University Management System",
    "nav_dashboard": "Dashboard",
    "nav_clubs": "Clubs",
    "nav_students": "Gifted Students",
    "nav_academic": "Faculties & Directions",
    "nav_settings": "Settings & Notifications",
    "logout": "Logout",

    // Dashboard
    "dash_title": "University Indicators",
    "dash_desc": "Overall statistics of gifted students and club activities",
    "refresh": "Refresh",
    "kpi_students": "Active Students",
    "kpi_waiting": "Waiting List (Queue)",
    "kpi_clubs": "Active Clubs",
    "kpi_faculties": "Faculties",
    "kpi_directions": "Study Directions",
    "faculty_distribution": "Distribution by Faculty",
    "top_clubs_fill": "Club Capacity Fill Rate (Top 6)",
    "recent_students_title": "Recently Enrolled Students",
    "recent_students_desc": "Latest registered or queued students",
    "no_recent_students": "No registered students yet.",
    "no_members_yet": "No members yet.",
    "no_data": "No data available.",
    "students_count_suffix": "students",
    "people_suffix": "people",

    // Table Headers
    "th_num": "№",
    "th_student_name": "Student Full Name",
    "th_club": "Club",
    "th_faculty": "Faculty",
    "th_direction": "Study Direction",
    "th_faculty_direction": "Faculty & Direction",
    "th_course": "Course",
    "th_status": "Status",
    "th_phone": "Phone Number",
    "th_telegram": "Telegram",
    "th_reg_date": "Registered At",
    "th_actions": "Actions",
    "th_leader": "Leader & Contact",
    "th_schedule": "Schedule Time",
    "th_capacity": "Capacity & Queue",
    "th_deadline": "Deadline",
    "th_code": "Code",
    "th_directions_count": "Directions Count",
    "th_clubs_count": "Clubs Count",

    // Badges & Statuses
    "status_active": "✅ Active Member",
    "status_waiting": "⏳ In Queue (#{pos})",
    "status_full": "🔒 Full ({cur}/{max} students | Queue: {wait})",
    "status_spots": "👥 {cur}/{max} members",
    "status_unlimited": "👥 {cur} members",
    "status_deadline_passed": "⛔ Deadline Passed ({date})",
    "status_deadline_open": "⏳ Deadline: {date}",

    // Clubs Tab
    "clubs_title": "Clubs Management",
    "clubs_desc": "List, capacity limits, and deadlines for all university scientific and creative clubs",
    "btn_add_club": "Add New Club",
    "btn_export": "Export",
    "export_excel": "📊 Excel (.xlsx)",
    "export_csv": "📄 CSV (.csv)",
    "filter_all_faculties": "All faculties",
    "filter_select_faculty": "Select faculty",
    "filter_select_direction": "Select direction",
    "filter_all_clubs": "All clubs",
    "no_clubs_found": "No clubs found.",
    "edit": "Edit",
    "delete": "Delete",
    "cancel_reg": "Cancel",
    "clubs_count_suffix": "{count} clubs",

    // Students Tab
    "students_title": "Gifted Students List",
    "students_desc": "Database of all students enrolled in clubs or waiting in queue",
    "search_student_placeholder": "Search by name or phone...",
    "filter_all_courses": "All courses",
    "filter_course_1": "1st year",
    "filter_course_2": "2nd year",
    "filter_course_3": "3rd year",
    "filter_course_4": "4th year",
    "filter_all_statuses": "All statuses",
    "filter_status_active": "Active members",
    "filter_status_waiting": "Waiting queue",
    "no_students_found": "No enrolled or waiting students found.",

    // Academic Tab
    "academic_title": "Faculties & Directions",
    "academic_desc": "Management of university faculties and academic specialties",
    "btn_add_faculty": "Add Faculty",
    "btn_add_direction": "Add Direction",
    "faculties_table_title": "Faculties List",
    "directions_table_title": "Study Directions List",
    "directions_count_badge": "{count} directions",

    // Settings Tab
    "settings_title": "System Settings & Notifications",
    "settings_desc": "Telegram channel integration and administrator security settings",
    "telegram_mgmt_card": "Telegram Management Channel",
    "telegram_mgmt_desc": "When students register for a club, applications are automatically forwarded to this channel.",
    "channel_id_label": "Channel Username or ID (e.g.: @universitet_iqtidorli or -1001234567890)",
    "btn_test_ping": "🔔 Send Test Notification",
    "btn_save": "Save",
    "admin_personal_tg": "Personal Telegram Notifications",
    "admin_personal_desc": "Enter your personal Telegram ID to receive direct application alerts from the bot.",
    "your_tg_id": "Your Telegram Chat ID",
    "security_card": "Security & Change Password",
    "security_desc": "Update administrator account password.",
    "current_password": "Current password",
    "new_password": "New password (at least 8 chars)",
    "confirm_password": "Confirm new password",
    "btn_update_password": "Update Password",
    "tg_guide_title": "Telegram Bot Quick Guide",
    "tg_step_1": "1. Open the bot on Telegram:",
    "tg_step_2": "2. Add the bot as an administrator to your channel with permission to post messages.",
    "tg_step_3": "3. Enter the channel username (@channel_name) or ID in the input on the left and click 'Save'.",
    "tg_step_4": "4. Click 'Send Test Notification' to verify connectivity.",

    // Modals
    "modal_add_club": "Add New Club",
    "modal_edit_club": "Edit Club",
    "form_club_direction": "Study Direction *",
    "form_club_name": "Club Name *",
    "form_club_name_placeholder": "E.g.: Young Programmers Club",
    "form_club_desc": "Club Description",
    "form_club_desc_placeholder": "About goals, tasks and activities of the club...",
    "form_club_days": "Schedule Days *",
    "form_club_days_placeholder": "E.g.: Tuesday, Thursday",
    "form_club_time": "Schedule Time *",
    "form_club_time_placeholder": "E.g.: 14:00 - 16:00",
    "form_club_room": "Room / Location *",
    "form_club_room_placeholder": "E.g.: Room 402, Building B",
    "form_club_leader": "Club Leader Full Name *",
    "form_club_leader_placeholder": "E.g.: Associate Prof. Aliyev B. A.",
    "form_club_contact": "Leader Contact *",
    "form_club_contact_placeholder": "E.g.: +998901234567 or @aliyev_leader",
    "form_club_max_cap": "Max Capacity (Quota)",
    "form_club_max_cap_hint": "Enter 0 for unlimited. When full, additional students will automatically be queued.",
    "form_club_deadline": "Registration Deadline",
    "form_club_deadline_hint": "Once the deadline passes, new registrations and queue entries are automatically closed.",
    "btn_cancel_modal": "Cancel",
    "btn_save_modal": "Save",

    "modal_add_faculty": "Add Faculty",
    "modal_edit_faculty": "Edit Faculty",
    "form_faculty_name": "Faculty Name *",
    "form_faculty_name_placeholder": "E.g.: Foreign Languages Faculty",
    "form_faculty_code": "Faculty Short Code",
    "form_faculty_code_placeholder": "E.g.: FLF",

    "modal_add_direction": "Add Direction",
    "modal_edit_direction": "Edit Direction",
    "form_direction_faculty": "Faculty *",
    "form_direction_name": "Direction Name *",
    "form_direction_name_placeholder": "E.g.: English Language and Literature",
    "form_direction_code": "Direction Code",
    "form_direction_code_placeholder": "E.g.: 60111800",

    // Confirmations & Toasts
    "confirm_delete_club": "Are you sure you want to delete this club? Associated student enrollments will also be removed.",
    "confirm_delete_faculty": "Are you sure you want to delete this faculty? Connected directions and clubs will also be deleted.",
    "confirm_delete_direction": "Are you sure you want to delete this direction?",
    "confirm_cancel_reg": "Are you sure you want to cancel this student's enrollment? If there are students in the queue, the next one will be automatically promoted with an instant Telegram notification.",
    "toast_data_refreshed": "Data refreshed successfully!",
    "toast_refresh_error": "Failed to refresh data",
    "toast_club_saved": "Club details updated",
    "toast_club_created": "New club created",
    "toast_club_deleted": "Club deleted successfully",
    "toast_faculty_saved": "Faculty saved",
    "toast_faculty_deleted": "Faculty deleted",
    "toast_direction_saved": "Direction saved",
    "toast_direction_deleted": "Direction deleted",
    "toast_channel_saved": "Management channel saved successfully!",
    "toast_chat_id_saved": "Telegram Chat ID saved successfully!",
    "toast_password_changed": "Password changed successfully!",
    "toast_password_mismatch": "New passwords do not match!",
    "toast_password_min_len": "New password must be at least 8 characters long!",

    // Login Page
    "login_page_title": "Login | University Gifted Students System",
    "login_brand_title": "Gifted Students System",
    "login_brand_subtitle": "University Admin Panel",
    "login_username_label": "Administrator Username",
    "login_password_label": "Password",
    "login_submit_btn": "Sign in to System",
    "login_error_invalid": "Invalid username or password!",
    "login_error_generic": "Error signing in",
    "logging_in": "Signing in..."
  }
};

// Global translation lookup
function t(key, params = {}) {
  const lang = getCurrentLanguage();
  const dict = I18N_TRANSLATIONS[lang] || I18N_TRANSLATIONS[DEFAULT_LANG];
  let text = dict[key] || I18N_TRANSLATIONS[DEFAULT_LANG][key] || key;
  
  if (params && typeof params === 'object') {
    Object.keys(params).forEach(k => {
      text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), params[k]);
    });
  }
  return text;
}

function getCurrentLanguage() {
  const saved = localStorage.getItem('admin_lang');
  return I18N_LANGUAGES.includes(saved) ? saved : DEFAULT_LANG;
}

function setLanguage(lang) {
  if (!I18N_LANGUAGES.includes(lang)) {
    lang = DEFAULT_LANG;
  }
  localStorage.setItem('admin_lang', lang);
  document.documentElement.lang = lang;

  // 1. Update text content
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.innerHTML = t(key);
  });

  // 2. Update placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    el.placeholder = t(key);
  });

  // 3. Update title attributes
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.getAttribute('data-i18n-title');
    el.title = t(key);
  });

  // 4. Update active state of language buttons
  document.querySelectorAll('.lang-pill').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
  });

  // 5. Update document title if marked
  const pageTitleEl = document.querySelector('title[data-i18n]');
  if (pageTitleEl) {
    document.title = t(pageTitleEl.getAttribute('data-i18n'));
  }

  // 6. Notify app.js to re-render dynamic content (dropdowns, table status badges, etc.)
  if (typeof window.onLanguageChanged === 'function') {
    window.onLanguageChanged(lang);
  }
}

// Auto-run on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  setLanguage(getCurrentLanguage());
});
