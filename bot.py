"""
بوت تليجرام لضغط ملفات PDF
يعتمد على Ghostscript لعمل الضغط الفعلي (تقليل حجم الصور والفونتات جوه الملف).

طريقة التشغيل:
    1) تأكد إن Ghostscript متثبت على جهازك (راجع ملف README.md).
    2) pip install -r requirements.txt
    3) حط التوكن بتاعك في متغير البيئة BOT_TOKEN أو في السطر تحت مباشرة.
    4) python bot.py
"""

import os
import subprocess
import logging
import tempfile

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ضع التوكن هنا أو خليه في متغير بيئة اسمه BOT_TOKEN
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ضع_التوكن_بتاعك_هنا")

# مستويات ضغط Ghostscript:
# /screen   -> أقل جودة وأصغر حجم (72 dpi)
# /ebook    -> جودة متوسطة، حجم أصغر بشكل كويس (150 dpi) - الافتراضي
# /printer  -> جودة أعلى (300 dpi)
# /prepress -> جودة عالية جدًا (300 dpi + ألوان)
QUALITY_PRESETS = {
    "screen": "/screen",
    "ebook": "/ebook",
    "printer": "/printer",
    "prepress": "/prepress",
}

MAX_FILE_SIZE_MB = 50  # حد تليجرام للبوتات العادية هو 20MB للتنزيل، خليها مرنة لو عندك API خاص


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً! ابعتلي ملف PDF وهضغطه وأرجعهولك.\n\n"
        "لو عايز تحدد مستوى الضغط ابعت الأمر:\n"
        "/quality screen  -> أصغر حجم ممكن (جودة أقل)\n"
        "/quality ebook   -> متوازن (الافتراضي)\n"
        "/quality printer -> جودة أعلى\n"
        "/quality prepress-> أعلى جودة"
    )


async def set_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0] not in QUALITY_PRESETS:
        await update.message.reply_text(
            "استخدم: /quality screen|ebook|printer|prepress"
        )
        return
    context.user_data["quality"] = context.args[0]
    await update.message.reply_text(f"تمام، مستوى الضغط دلوقتي: {context.args[0]}")


def compress_pdf(input_path: str, output_path: str, quality: str = "ebook") -> None:
    gs_setting = QUALITY_PRESETS.get(quality, "/ebook")
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={gs_setting}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Ghostscript error: {result.stderr}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if doc is None or not (doc.file_name or "").lower().endswith(".pdf"):
        await update.message.reply_text("ابعتلي ملف PDF بس من فضلك.")
        return

    size_mb = (doc.file_size or 0) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        await update.message.reply_text(
            f"الملف كبير أوي ({size_mb:.1f}MB). الحد الأقصى {MAX_FILE_SIZE_MB}MB."
        )
        return

    quality = context.user_data.get("quality", "ebook")
    status_msg = await update.message.reply_text("جاري تحميل الملف وضغطه... ⏳")

    with tempfile.TemporaryDirectory() as tmp_dir:
        input_path = os.path.join(tmp_dir, "input.pdf")
        output_path = os.path.join(tmp_dir, "compressed.pdf")

        tg_file = await doc.get_file()
        await tg_file.download_to_drive(input_path)

        try:
            compress_pdf(input_path, output_path, quality)
        except Exception as e:
            logger.exception("فشل الضغط")
            await status_msg.edit_text(f"حصل خطأ أثناء الضغط: {e}")
            return

        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)

        if compressed_size >= original_size:
            # أحيانًا الملف يكون مضغوط أصلاً ومفيش فايدة من إعادة الضغط
            await status_msg.edit_text(
                "الملف مضغوط أصلاً ومفيش تحسين ممكن، هبعتلك نفس الملف."
            )
            final_path = input_path
        else:
            saved_pct = (1 - compressed_size / original_size) * 100
            await status_msg.edit_text(
                f"تم الضغط ✅\n"
                f"الحجم قبل: {original_size / 1024:.0f} KB\n"
                f"الحجم بعد: {compressed_size / 1024:.0f} KB\n"
                f"نسبة التوفير: {saved_pct:.1f}%"
            )
            final_path = output_path

        with open(final_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"compressed_{doc.file_name}",
            )


def main():
    if BOT_TOKEN == "ضع_التوكن_بتاعك_هنا":
        raise SystemExit(
            "لازم تحط توكن البوت الأول (متغير بيئة BOT_TOKEN أو في الكود مباشرة)."
        )

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quality", set_quality))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    logger.info("البوت شغال...")
    app.run_polling()


if __name__ == "__main__":
    main()
