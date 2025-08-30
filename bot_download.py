import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8197996560:AAFshyi0AYVcVULxwAANzNBz9RM7-9Y9kHc"
CHANNEL_USERNAME = "@p_y_hy" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ حتى تقدر تستخدم البوت، اشترك أولًا بالقناة: {CHANNEL_USERNAME}"
        )
        return

    welcome_text = """
اهلابيك حبيبي في بوت تحميل الفيديوهات!🌟
أرسل لي رابط الفيديو من أي منصة وأنا أحمله إلك!

📌 ملاحظة: بعض فيديوهات اليوتيوب قد لا تعمل بسبب القيود
    """
    await update.message.reply_text(welcome_text)

async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"خطأ أثناء التحقق من الاشتراك: {e}")
        return False

def download_video(url):
    """دورة التحميل المعدلة لليوتيوب"""
    ydl_opts = {
        'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Connection': 'keep-alive',
        },
        'no_check_certificate': True,
        'ignoreerrors': True,
        'quiet': False,
        'verbose': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, None
    except Exception as e:
        return None, str(e)

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ حتى تقدر تستخدم البوت، اشترك أولًا بالقناة: {CHANNEL_USERNAME}"
        )
        return

    url = update.message.text.strip()
    
    # فحص إذا كان الرابط من اليوتيوب
    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("🎬 جاري تحميل من اليوتيوب... (قد يأخذ وقت)")
    else:
        await update.message.reply_text("⏳ جاري التحميل...")

    try:
        filename, error = download_video(url)
        
        if error:
            if "Private video" in error:
                await update.message.reply_text("❌ الفيديو خاص ولا يمكن تحميله")
            elif "Members only" in error:
                await update.message.reply_text("❌ الفيديو للأعضاء فقط")
            elif "Sign in" in error:
                await update.message.reply_text("❌ الفيديو يتطلب تسجيل دخول")
            elif "age restricted" in error.lower():
                await update.message.reply_text("❌ الفيديو محظور بسبب العمر")
            else:
                await update.message.reply_text(f"❌ فشل التحميل: {error}")
            return

        if filename and os.path.exists(filename):
            await update.message.reply_text("✅ تم التحميل! جاري الإرسال...")
            
            # إرسال الفيديو
            with open(filename, "rb") as video:
                await update.message.reply_video(
                    video, 
                    caption="📥 تم التحميل بنجاح"
                )
            
            # حذف الملف بعد الإرسال
            os.remove(filename)
        else:
            await update.message.reply_text("❌ لم يتم إنشاء الملف، حاول برابط آخر")

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ غير متوقع: {str(e)}")

if not os.path.exists("downloads"):
    os.makedirs("downloads")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))

print("🚀 البوت يشتغل...")
app.run_polling()
