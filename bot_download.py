import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ====== إعداد التوكن واسم القناة ======
TOKEN = "8197996560:AAFshyi0AYVcVULxwAANzNBz9RM7-9Y9kHc"
CHANNEL_USERNAME = "@p_y_hy"

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
        print(f"خطأ أثناء التحقق من الاشتراك: {e}")
        return False

# ====== دالة تحميل الفيديو ======
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

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

        os.remove(filename)

    except Exception as e:
        error_msg = str(e)
        if "Sign in" in error_msg or "cookies" in error_msg:
            await update.message.reply_text(
                "❌ لم أستطع تحميل الفيديو. يبدو أن المنصة تطلب تحقق.\n\n"
                "📥 جرب روابط من:\n"
                "• تيك توك 🎵\n"
                "• فيسبوك 👍\n"
                "• تويتر 🐦\n"
                "• إنستغرام 📸 (قد يعمل أحياناً)"
            )
        else:
            await update.message.reply_text(f"❌ صار خطأ أثناء التحميل: {error_msg}")

# ====== الإعدادات الرئيسية ======
if not os.path.exists("downloads"):
    os.makedirs("downloads")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))

print("🚀 البوت يشتغل...")
app.run_polling()
