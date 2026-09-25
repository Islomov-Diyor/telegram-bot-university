# 🚀 Loyihani Bepul Hostingga Joylashtirish Bo'yicha To'liq Qo'llanma

Ushbu qo'llanma orqali siz loyihangizni ertaga **Render.com** (eng oson va 100% bepul) yoki boshqa bepul platformalarga 5 daqiqada joylashtirishingiz mumkin.

---

## 🏆 1-USUL: Render.com (Tavsiya etiladi — 100% Bepul va Avtomatik)

Render.com har oy bepul server resurslarini taqdim etadi va GitHub repozitoriyangiz bilan avtomatik bog'lanadi.

### 1-qadam: Ro'yxatdan o'tish
1. [https://render.com](https://render.com) saytiga kiring.
2. **"Sign In"** -> **"GitHub bilan kirish"** (Sign in with GitHub) tugmasini bosing.

### 2-qadam: Yangi Web Service yaratish
1. Render bosh sahifasida **"New +"** tugmasini bosing va **"Web Service"** ni tanlang.
2. **"Build and deploy from a Git repository"** ni tanlang.
3. GitHub repozitoriyangizni tanlang:
   `https://github.com/Islomov-Diyor/telegram-bot-university`
   *(Agar ro'yxatda ko'rinmasa, "Configure account" orqali repozitoriyaga ruxsat bering)*.

### 3-qadam: Sozlamalarni kiritish
Quyidagi parametrlarni to'ldiring:
* **Name:** `university-talented-students` (yoki ixtiyoriy nom)
* **Region:** `Frankfurt (EU Central)` yoki `Singapore` (O'zbekistonga eng yaqin)
* **Branch:** `main`
* **Root Directory:** *(bo'sh qoldiring)*
* **Runtime:** `Python 3`
* **Build Command:**
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt
  ```
* **Start Command:**
  ```bash
  uvicorn src.main:app --host 0.0.0.0 --port $PORT
  ```
* **Instance Type:** **Free** ($0 / month)

### 4-qadam: Environment Variables (Muhit O'zgaruvchilari)
Pastga tushib, **"Environment Variables"** bo'limida quyidagi o'zgaruvchilarni qo'shing:

| Key | Value (Namuna) | Izoh |
| :--- | :--- | :--- |
| `BOT_TOKEN` | `<SIZNING_TELEGRAM_BOT_TOKENINGIZ>` | @BotFather bergan bot tokeni |
| `ADMIN_USERNAME` | `admin` | Admin panel uchun o'zingiz xohlagan login |
| `ADMIN_PASSWORD` | `<SIZNING_XAVFSIZ_PAROLINGIZ>` | Admin panel uchun o'zingiz belgilaydigan kuchli parol |
| `ADMIN_CHANNEL_ID` | `@sizning_kanalingiz` | Telegram boshqaruv kanali username yoki chat ID |
| `SECRET_KEY` | `<IXTIYORIY_UZUN_MAXFIY_KALIT>` | JWT xavfsizlik kaliti (masalan: 32+ belgili tasodifiy matn) |
| `DEBUG` | `False` | Ishlab chiqarish rejimi |

### 5-qadam: Ishga tushirish (Deploy)
* **"Create Web Service"** tugmasini bosing.
* Render 2-3 daqiqada kutubxonalarni o'rnatib, bot va veb-saytni ishga tushiradi!
* Render sizga bepul HTTPS domen beradi, masalan:
  `https://university-talented-students.onrender.com/login`
* **Natija:** Telegram Bot ham, Web Admin Panel ham 24/7 rejimda, kompyuteringiz yopiq bo'lsa ham uzluksiz ishlaydi!

---

## 💻 2-USUL: O'z Kompyuteringizda IDE'siz (Antigravity'siz) 1-bosishda Ishlatish

Agar hostingga qo'ymasdan turib, o'z kompyuteringizda Antigravity IDE'ni butunlay yopgan holda ishlatmoqchi bo'lsangiz:

1. Loyiha papkasiga kiring:
   `c:\Users\user\Desktop\telegram bot for universitey of foreign`
2. **`start_app.bat`** faylini ikki marta bosing (Double click).
3. Ushbu skript:
   * Avtomatik ravishda serverni va Telegram botni ishga tushiradi.
   * Brauzeringizda `http://localhost:8000/login` manzilini ochadi.
4. Serverni to'xtatish uchun qora konsol oynasida `Ctrl + C` bosish kifoya.
