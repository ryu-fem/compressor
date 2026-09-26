# بوت تليجرام لضغط ملفات PDF

بوت بسيط يشتغل على جهازك (local) يستقبل ملف PDF ويرجعلك نسخة مضغوطة منه.

## المتطلبات

### 1. Ghostscript (المسؤول عن الضغط الفعلي)
لازم يكون متثبت على جهازك:

- **Windows**: نزّل من https://ghostscript.com/releases/gsdnld.html وتأكد إن الأمر `gswin64c` أو `gs` شغال من الـ terminal (أو عدّل اسم الأمر جوه `bot.py` من `gs` لـ `gswin64c` لو لزم الأمر).
- **macOS**: `brew install ghostscript`
- **Linux (Ubuntu/Debian)**: `sudo apt install ghostscript`

تأكد إنه اتثبت صح بكتابة:
```
gs --version
```

### 2. مكتبات بايثون
```
pip install -r requirements.txt
```

## إنشاء البوت والحصول على التوكن

1. افتح تليجرام وابحث عن `@BotFather`.
2. ابعتله `/newbot` واتبع الخطوات (اختار اسم ويوزرنيم للبوت).
3. هيديك توكن شكله زي كده: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`.

## التشغيل

حط التوكن كمتغير بيئة (الأفضل أمنيًا):

**Linux/macOS:**
```
export BOT_TOKEN="التوكن_بتاعك"
python bot.py
```

**Windows (PowerShell):**
```
$env:BOT_TOKEN="التوكن_بتاعك"
python bot.py
```

أو ببساطة افتح `bot.py` وحط التوكن مكان `"ضع_التوكن_بتاعك_هنا"` مباشرة.

## طريقة الاستخدام

1. افتح شات البوت على تليجرام واضغط Start.
2. ابعت `/quality ebook` (أو screen / printer / prepress) لو عايز تحدد مستوى الضغط، وإلا هيستخدم `ebook` كافتراضي.
3. ابعت ملف PDF كـ **Document** (مش كصورة).
4. البوت هيرد عليك بالملف المضغوط + نسبة التوفير في الحجم.

## النشر على Railway (بدل تشغيله لوكال)

عشان البوت يفضل شغال 24/7 من غير ما تسيب جهازك مفتوح، ارفعه على Railway:

### 1. جهّز مستودع Git
حط الملفات دي كلها في مجلد واحد وارفعها على GitHub (repo عادي، ممكن يكون private):
- `bot.py`
- `requirements.txt`
- `nixpacks.toml`  (بيقول لـ Railway إنه يثبت Ghostscript وقت البناء)
- `Procfile`       (بيقول لـ Railway إن السيرفس ده "worker" مش "web")

**مهم:** متحطش التوكن جوه الكود أو جوه الـ repo خالص، هنحطه كـ Environment Variable في الخطوة الجاية.

### 2. اعمل مشروع جديد على Railway
1. ادخل https://railway.app وسجل دخول (فيه ربط مباشر بـ GitHub).
2. اضغط **New Project** → **Deploy from GitHub repo** → اختار الـ repo بتاعك.
3. Railway هيكتشف إنه مشروع Python ويستخدم Nixpacks تلقائيًا، وهيقرأ ملف `nixpacks.toml` عشان يثبت Ghostscript جنب مكتبات بايثون.

### 3. ضيف متغير البيئة (التوكن)
جوه المشروع في Railway:
- روح تبويب **Variables**.
- ضيف متغير اسمه `BOT_TOKEN` وقيمته توكن البوت اللي جبته من BotFather.

### 4. تأكد إن السيرفس شغال كـ Worker مش Web
البوت بيستخدم `run_polling()` يعني مش محتاج يفتح بورت أو يستقبل HTTP requests. Railway ممكن يحاول يعامله كـ "web service" وينتظر بورت مفتوح، فلو حصل مشكلة:
- روح **Settings** بتاع السيرفس وشيل أي "Public Networking / Domain" (مش محتاجينه).
- تأكد إن أمر التشغيل (Start Command) هو `python bot.py` (Railway هياخده من `Procfile` تلقائيًا).

### 5. Deploy وتابع الـ Logs
اضغط **Deploy**، وبعدين افتح تبويب **Logs** وتأكد إنك شايف رسالة `البوت شغال...` من غير أخطاء. لو حصل خطأ خاص بـ `gs: command not found`، يبقى `nixpacks.toml` مترفعش صح — تأكد إنه في نفس مجلد `bot.py` بالظبط.

### 6. تكلفة
Railway بيدي رصيد مجاني شهري محدود، وبعده بيتحاسب حسب الاستخدام (وقت تشغيل + رام). بوت بسيط زي ده استهلاكه قليل، لكن لازم تتابع الفوترة من تبويب **Usage**.

## دعم الملفات الأكبر من 20MB (Local Bot API Server)

سيرفرات تليجرام العادية بتحدد تحميل الملفات بـ **20MB** حتى لو البوت بيدعم أكبر من كده. عشان تتعامل مع ملفات لحد **2GB** لازم تشغّل سيرفر تليجرام محلي بنفسك (Local Bot API Server) وتوصّل البوت بيه. جهّزنالك ده جاهز بـ Docker Compose.

### 1. جيب api_id و api_hash
1. ادخل https://my.telegram.org وسجل دخول برقمك.
2. اختار **API development tools**.
3. اعمل تطبيق جديد (أي اسم)، وهيديك `api_id` و `api_hash`.

### 2. جهّز متغيرات البيئة
اعمل ملف `.env` جنب `docker-compose.yml`:
```
BOT_TOKEN=توكن_البوت_من_BotFather
TELEGRAM_API_ID=الرقم_اللي_جالك
TELEGRAM_API_HASH=الكود_اللي_جالك
```

### 3. شغّل الستاك
```
docker compose up -d --build
```

ده هيشغّل حاجتين:
- **telegram-bot-api**: سيرفر تليجرام المحلي، بيرفع الحد لـ 2GB.
- **pdf-bot**: بوت الضغط نفسه، متوصّل بالسيرفر المحلي بدل سيرفرات تليجرام العادية.

الاتنين بيشاركوا نفس الـ volume (`bot-api-data`) عشان بوت بايثون يقدر يوصل للملفات اللي السيرفر نزلها من غير ما يعيد تحميلها بنفسه.

### 4. تابع الـ logs
```
docker compose logs -f pdf-bot
```

### ملاحظة عن Railway
شرحنا فوق طريقة docker-compose (سيرفيسين منفصلين) وده الأنسب لـ VPS. تحت طريقة مخصوصة لـ Railway في كونتينر واحد.

## دعم الملفات الكبيرة على Railway (كل حاجة في كونتينر واحد)

Railway مبيدعمش مشاركة volume بسهولة بين سيرفيسين، فالحل إن `telegram-bot-api` والبوت يشتغلوا **جوه نفس الكونتينر**. جهّزنالك:
- `Dockerfile.railway`: بيبني `telegram-bot-api` من المصدر الرسمي (تدلib) ويحطه جنب بايثون و Ghostscript.
- `start.sh`: بيشغّل السيرفر المحلي في الخلفية وبعدين البوت.

### 1. ارفع الملفات على GitHub
لازم يكون موجود في الـ repo: `bot.py`, `requirements.txt`, `Dockerfile.railway`, `start.sh`.

### 2. اربط الـ repo بـ Railway
1. **New Project** → **Deploy from GitHub repo**.
2. روح **Settings** بتاع السيرفس → **Build** → غيّر **Dockerfile Path** لـ `Dockerfile.railway` (بدل الافتراضي `Dockerfile`، عشان متتعارضش مع الملف التاني اللي لو مستخدم docker-compose لوحده).
   - لو مفيش عندك ملف `Dockerfile` تاني في نفس الـ repo أصلاً، ممكن تسمي الملف `Dockerfile` عادي وتسيب Railway يكتشفه لوحده من غير ما تغيّر أي إعداد.

### 3. ضيف متغيرات البيئة
في تبويب **Variables**:
```
BOT_TOKEN=توكن_البوت
TELEGRAM_API_ID=الرقم_من_my.telegram.org
TELEGRAM_API_HASH=الكود_من_my.telegram.org
MAX_FILE_SIZE_MB=1900
```

### 4. شيل الـ Public Networking
البوت شغال بـ polling، مش محتاج بورت مفتوح للعالم الخارجي — احذف أي Domain من **Settings → Networking**.

### 5. (اختياري) ضيف Volume
عشان الملفات المؤقتة متضيعش لو الكونتينر أعيد تشغيله فجأة أثناء عملية ضغط:
- روح **Settings → Volumes** وأضف Volume على المسار `/data`.
- ده مش إجباري، لكنه بيحسّن الاستقرار مع الملفات الكبيرة.

### 6. Deploy وتابع الـ Logs
أول Build هياخد وقت أطول من المعتاد (بيبني `telegram-bot-api` من الصفر، ممكن ياخد 10-15 دقيقة)، البنيات اللي بعد كده هتبقى أسرع بسبب الـ cache. تابع الـ Logs وتأكد إنك شايف رسالة `البوت شغال...` بعد ما سيرفر تليجرام يشتغل.

## ملاحظات

- مستوى `screen` بيدي أصغر حجم لكن جودة أقل (مناسب لو الملف فيه صور كتير).
- مستوى `prepress` بيحافظ على جودة عالية لكن التوفير في الحجم بيكون أقل.
- تليجرام بيحدد حجم الملفات اللي البوت العادي يقدر ينزلها بـ 20MB تقريبًا؛ لو محتاج ملفات أكبر لازم تستخدم Local Bot API Server.
- الكود بيمسح الملفات المؤقتة أوتوماتيك بعد كل عملية (مفيش تخزين دائم لملفاتك).
