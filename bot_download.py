import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import tempfile
import asyncio

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ====== إعداد التوكن واسم القناة ======
TOKEN = os.environ.get("BOT_TOKEN", "8197996560:AAFshyi0AYVcVULxwAANzNBz9RM7-9Y9kHc")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@p_y_hy")

# ====== دالة بدء التشغيل ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ حتى تقدر تستخدم البوت، اشترك أولًا بالقناة: {CHANNEL_USERNAME}"
        )
        return

    await update.message.reply_text("اهلابيك حبيبي في بوت احمد خان!🌟\nأرسل لي رابط الفيديو من أي منصة وأنا أحمله إلك!")

# ====== دالة التحقق من الاشتراك بالقناة ======
async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"خطأ أثناء التحقق من الاشتراك: {e}")
        return False

# ====== دالة تحميل الفيديو ======
def download_video(url):
    # إنشاء مجلد مؤقت داخل /tmp
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'format': 'best[filesize<20M]',  # حجم أصغر ليتناسب مع GitHub
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        # تنظيف المجلد المؤقت في حالة الخطأ
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise e

# ====== دالة معالجة التحميل ======
async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ حتى تقدر تستخدم البوت، اشترك أولًا بالقناة: {CHANNEL_USERNAME}"
        )
        return

    url = update.message.text
    await update.message.reply_text("⏳ جاري التحميل، انتظر شوي...")

    try:
        filename = download_video(url)
        await update.message.reply_text("✅ تم التحميل! جاري الإرسال...")

        with open(filename, "rb") as video:
            await update.message.reply_video(video)

        # تنظيف الملفات المؤقتة
        try:
            os.remove(filename)
            temp_dir = os.path.dirname(filename)
            if temp_dir.startswith('/tmp'):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

    except Exception as e:
        error_msg = str(e)
        logging.error(f"خطأ في التحميل: {error_msg}")
        
        if "Sign in" in error_msg or "cookies" in error_msg:
            await update.message.reply_text(
                "❌ لم أستطع تحميل الفيديو. يبدو أن المنصة تطلب تحقق.\n\n"
                "📥 جرب روابط من:\n"
                "• تيك توك 🎵\n"
                "• فيسبوك 👍\n"
                "• تويتر 🐦\n"
            )
        else:
            await update.message.reply_text(f"❌ صار خطأ أثناء التحميل: {error_msg}")

# ====== الإعدادات الرئيسية ======
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))

    logging.info("🚀 البوت يشتغل على GitHub Actions...")
    
    # تشغيل البوت مع إعادة التشغيل التلقائي
    while True:
        try:
            app.run_polling()
        except Exception as e:
            logging.error(f"البوت توقف: {e}. إعادة التشغيل خلال 10 ثوان...")
            time.sleep(10)

if __name__ == "__main__":
    main()
