# ⚽ FootballIQ — Professional Football Quiz Telegram Bot

**FootballIQ** — futbol muxlislari uchun bilim platformasi.  
Viktorinalar, Guess the Player/Club, Daily Challenge, XP tizimi, reytinglar va ko‘proq.

Barcha asosiy funksiyalar **BEPUL**.

---

## 🚀 Tez boshlash (Windows / PowerShell)

### 1. Talablar
- Python 3.10+ (tavsiya 3.11 yoki 3.12)
- Telegram Bot Token (@BotFather dan oling)

### 2. O‘rnatish

```powershell
# Loyihani yuklab oling va papkaga kiring
cd FootballIQ

# Virtual environment (tavsiya etiladi)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Kutubxonalarni o‘rnating
pip install -r requirements.txt
```

### 3. Sozlash

`.env.example` faylini nusxalang va `.env` deb saqlang:

```powershell
Copy-Item .env.example .env
```

`.env` faylini oching va to‘ldiring:

```
BOT_TOKEN=123456:ABC-your-real-token
ADMIN_IDS=your_telegram_id
DATABASE_URL=sqlite+aiosqlite:///footballiq.db
LOG_LEVEL=INFO
```

> O‘z Telegram ID ingizni bilish uchun @userinfobot ga yozing.

### 4. Savollarni yuklash

```powershell
python load_questions.py
```

Bu buyruq 70+ tekshirilgan savollarni bazaga yuklaydi (turli kategoriyalar va qiyinliklar).

### 5. Botni ishga tushirish

```powershell
python bot.py
```

Bot ishga tushgach Telegramda `/start` yuboring.

---

## 📁 Loyiha strukturasi

```
FootballIQ/
├── bot.py                 # Asosiy kirish nuqtasi
├── config.py              # Sozlamalar
├── load_questions.py      # Savollarni DB ga yuklash
├── requirements.txt
├── .env.example
├── README.md
│
├── handlers/              # Barcha handlerlar
│   ├── start.py
│   ├── menu.py
│   ├── quiz.py
│   ├── daily_challenge.py
│   ├── profile.py
│   └── admin.py
│
├── keyboards/             # Tugmalar
├── database/              # SQLAlchemy modellar va so‘rovlar
├── services/              # Biznes mantiq (quiz, XP, ranking...)
├── locales/               # uz / en / ru tarjimalar
├── data/                  # Qo‘shimcha JSON (kengaytirish uchun)
└── utils/
```

---

## 🎮 Asosiy imkoniyatlar

| Funksiya              | Holat      | Izoh                          |
|-----------------------|------------|-------------------------------|
| Football Quiz         | ✅ Ishlaydi | 16 kategoriya + 4 qiyinlik   |
| Guess the Player      | ✅         | Players kategoriyasi orqali  |
| Guess the Club        | ✅         | Clubs kategoriyasi           |
| National Teams        | ✅         |                               |
| Football History      | ✅         |                               |
| Tactical Quiz         | ✅         |                               |
| Daily Challenge       | ✅         | Kuniga 1 marta, bonus XP     |
| 1 vs 1 Battle         | ⏳         | Keyingi versiyada            |
| Rankings              | ✅         | Global XP reyting            |
| Profile + XP + Level  | ✅         |                               |
| 3 til (UZ/EN/RU)      | ✅         |                               |
| Admin panel           | ✅         | /admin, /broadcast, /block   |

---

## 🛠 Admin buyruqlari

Faqat `ADMIN_IDS` dagi foydalanuvchilar:

- `/admin` — panel
- `/stats` — statistika
- `/broadcast <matn>` — barcha foydalanuvchilarga xabar
- `/block <user_id>` / `/unblock <user_id>`

---

## 📈 Savollar bazasini kengaytirish

`load_questions.py` ichidagi `QUESTIONS` ro‘yxatiga yangi savollar qo‘shing yoki JSON orqali yuklash funksiyasini kengaytiring.

Har bir savol uchun:
- 3 tilda savol matni
- 3 tilda 4 ta variant
- To‘g‘ri javob indeksi (0-3)
- Qisqa izoh (3 tilda)
- Kategoriya va qiyinlik

Keyin:

```powershell
# Eski bazani o‘chirish (ixtiyoriy)
Remove-Item footballiq.db -ErrorAction SilentlyContinue

python load_questions.py
python bot.py
```

---

## ⚙️ Texnologiyalar

- Python 3.10+
- **aiogram 3**
- SQLAlchemy 2 + aiosqlite (SQLite)
- python-dotenv
- APScheduler (kelajakdagi kunlik vazifalar uchun)
- Pillow

**Hech qanday pullik API ishlatilmagan.**

---

## 📌 Eslatmalar

- Bot qayta ishga tushganda ma’lumotlar saqlanib qoladi (SQLite).
- Bir savolga bir necha marta javob berib XP olishning oldi olingan.
- Savollar foydalanuvchiga yaqinda berilganlarini kamaytirib tanlanadi.
- 1v1 Battle va ba’zi kengaytmalar keyingi yangilanishlarda to‘liq ishga tushadi.

---

**FootballIQ** — futbol bilimdonlari uchun yaratilgan.  
Savollaringiz va g‘oyalaringiz bilan bazani boyiting!

⚽ Good luck & enjoy the game!
