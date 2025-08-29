import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import time
import logging

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# الحصول على التوكن من متغيرات البيئة
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")

if not TOKEN:
    logging.error("❌ ERROR: BOT_TOKEN not found!")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أهلاً! بيك في بوت احمد خان أرسل لي رابط فيديو وسأحمله لك!")

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = update.message.text
        await update.message.reply_text("⏳ جاري التحميل...")
        
        filename = download_video(url)
        await update.message.reply_text("✅ تم التحميل! جاري الإرسال...")

        with open(filename, "rb") as video:
            await update.message.reply_video(video)

        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

def main():
    # إنشاء مجلد التحميلات
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))

    logging.info("🚀 Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
