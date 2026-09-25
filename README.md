# UNIVERSITET IQTIDORLI TALABALAR BOTI VA BOSHQARUV PANELI

Ushbu platforma universitet iqtidorli talabalarini fakultet va ta'lim yo'nalishlari kesimidagi ilmiy, ijodiy va fan to'garaklariga jalb qilish, ularni ro'yxatga olish, saralash hamda to'garak faoliyatlarini markazlashgan holda boshqarish tizimidir.

---

## 🌟 Asosiy Imkoniyatlar

### 🤖 Telegram Bot (Talabalar uchun)
1. **Fakultet va Yo'nalish tanlash**: Talaba o'z fakultetini tanlaydi, so'ngra shu fakultetga tegishli yo'nalishlar dinamik chiqadi.
2. **To'garaklar katalogi**: Tanlangan yo'nalish bo'yicha mavjud to'garaklar (nomi, tavsifi, kunlari, vaqti, xonasi, rahbari va aloqa ma'lumotlari).
3. **Qulay ro'yxatdan o'tish (FSM)**:
   - Ism-familiya kiritish (kamida 2 ta so'z tekshiruvi);
   - Fakultet va yo'nalish avtomatik biriktiriladi;
   - Kursni tanlash (1, 2, 3, 4-kurs);
   - Telefon raqamni tugma orqali ulashish yoki yozish;
   - Telegram username avtomatik aniqlanadi;
   - Barcha ma'lumotlarni ko'rib tasdiqlash.
4. **Duplikat arizalarni bloklash**: Bir talaba ayni bir to'garakka bir necha marta ro'yxatdan o'ta olmaydi.
5. **Avtomatik administrator bildirishnomasi**: Har bir yangi talaba ro'yxatdan o'tgan zahoti belgilangan administrator(lar)ga Telegram orqali barcha ma'lumotlar bilan chiroyli xabar boradi.

### 💻 Web Admin Panel (Universitet Ma'muriyati uchun)
1. **Zamonaviy Dashboard**: Talabalar soni, faol to'garaklar, eng ommabop to'garaklar reytingi, fakultetlar kesimidagi taqsimot.
2. **To'garaklar boshqaruvi (CRUD)**:
   - Yangi to'garak ochish;
   - Mashg'ulot kunlari va vaqtini o'zgartirish;
   - Xona va joylashuvni o'zgartirish;
   - Rahbar va uning aloqa ma'lumotlarini tahrirlash;
   - Har bir to'garakdagi talabalar sonini ko'rish.
3. **Talabalar jurnali**:
   - Talaba F.I.Sh, fakultet, yo'nalish, kurs, telefon va Telegram usernamesi;
   - Tezkor qidiruv va filtrlar (fakultet, yo'nalish, kurs);
   - Talabani to'garakdan chiqarish / bekor qilish.
4. **Eksport moduli**:
   - 📥 **Microsoft Excel (.xlsx)**: Stillangan sarlavhalar, navy blue dizayn va moslashtirilgan ustun kengliklari bilan;
   - 📄 **CSV (.csv)**: O'zbekcha harflar (o‘, g‘, sh, ch) buzilmasligi uchun UTF-8 BOM bilan.
5. **Akademik boshqaruv**: Fakultet va ta'lim yo'nalishlarini qo'shish, tahrirlash va o'chirish.
6. **Telegram Chat ID sozlash**: Admin o'z shaxsiy chat ID'sini panel orqali kiritib qo'yishi mumkin.

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.10 yoki 3.11+
- Git

### 2. Virtual muhit yaratish va kutubxonalarni o'rnatish
```bash
# Virtual muhit yaratish
python -m venv venv

# Virtual muhitni faollashtirish:
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

### 3. Konfiguratsiya (.env)
Lokal sozlash uchun `.env.example` faylidan nusxa olib, `.env` faylini yarating va kerakli parametrlarni (Bot token va xavfsiz admin parolini) kiriting:
```bash
# Windows:
copy .env.example .env

# Linux/macOS:
cp .env.example .env
```

### 4. Dasturni ishga tushirish
Dastur ishga tushganda barcha kerakli jadvallar va dastlabki ma'lumotlar avtomatik ravishda tayyorlanadi:
```bash
python -m src.main
```
*Windows foydalanuvchilari uchun loyiha ildizidagi `start_app.bat` faylini 1 bosish orqali ishga tushirish ham mumkin.*

Ishga tushgach:
- 🌐 **Web Admin Panel:** [http://localhost:8000/login](http://localhost:8000/login)
- 📚 **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- 🤖 **Telegram Bot:** Telegramda o'z botingizga `/start` yuborib tekshirishingiz mumkin.

---

## 🗄 SQLite'dan PostgreSQL'ga Ko'chirish

Loyiha to'liq `SQLAlchemy 2.0 (asyncio)` ustiga qurilgan. PostgreSQL'ga o'tish uchun:
1. PostgreSQL drayverini o'rnating:
   ```bash
   pip install asyncpg
   ```
2. `.env` faylidagi bitta qatorni o'zgartiring:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:parol@localhost:5432/university_clubs
   ```
Barcha modellar va so'rovlar hech qanday o'zgarishsiz avtomatik ishlayveradi!

---

## 🐳 Docker Orqali Ishga Tushirish

```bash
# Konteynerni yig'ish va ishga tushirish
docker-compose up -d --build

# Loglarni ko'rish
docker-compose logs -f
```

---

## ☁️ Bepul Hosting Variantlari

1. **Universitetning o'z kompyuteri / Serveri (Tavsiya etiladi - 0 so'm):**
   - Kompyuterga Docker yoki Python o'rnatiladi;
   - [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) (mutlaqo bepul) orqali oq IP kerak bo'lmagan holda bepul HTTPS domen beriladi.
2. **Oracle Cloud Always Free Tier:**
   - 4 OCPU, 24 GB RAM (Umrbod bepul VPS).
3. **Render.com:**
   - Web Service sifatida GitHub reposini ulab bir necha daqiqada ishga tushirish mumkin.
