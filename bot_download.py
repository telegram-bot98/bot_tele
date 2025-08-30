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
اهلابيك حبيبي في بوت احمد خان!🌟
أرسل لي رابط الفيديو من أي منصة وأنا أحمله إلك!

📌 للإستخدام:
• أرسل الرابط مباشرة لتحميل أفضل جودة
• أو استخدم /download <رابط> لاختيار الجودة
    """
    await update.message.reply_text(welcome_text)

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ حتى تقدر تستخدم البوت، اشترك أولًا بالقناة: {CHANNEL_USERNAME}"
        )
        return
    
    if not context.args:
        await update.message.reply_text("📝 Usage: /download <URL>")
        return
    
    url = context.args[0]
    await handle_download(update, url, quality_choice=True)

async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"خطأ أثناء التحقق من الاشتراك: {e}")
        return False

def get_video_formats(url):
    """الحصول على قائمة التنسيقات المتاحة"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
        'listformats': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

def download_video(url, format_id=None):
    ydl_opts = {
        'format': format_id or 'best[height<=720]',  # أفضل جودة حتى 720p
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',  # دمج الصوت والفيديو بصيغة mp4
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        'verbose': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

async def handle_download(update: Update, url: str, quality_choice: bool = False):
    try:
        await update.message.reply_text("⏳ جاري التحضير، انتظر شوي...")
        
        # إذا كان من اليوتيوب ونريد اختيار الجودة
        if "youtube.com" in url or "youtu.be" in url" and quality_choice:
            try:
                formats = get_video_formats(url)
                # هنا يمكن إضافة منطق لاختيار الجودة
                # للتبسيط سنستخدم جودة متوسطة
                format_id = 'best[height<=720]'
            except:
                format_id = 'best'
        else:
            format_id = 'best'
        
        await update.message.reply_text("⏳ جاري التحميل، انتظر شوي...")
        
        filename = download_video(url, format_id)
        await update.message.reply_text("✅ تم التحميل! جاري الإرسال...")

        # إرسال الفيديو
        with open(filename, "rb") as video:
            await update.message.reply_video(
                video, 
                caption="✅ تم التحميل بواسطة @BotDownloader"
            )

        # حذف الملف بعد الإرسال
        os.remove(filename)

    except yt_dlp.utils.DownloadError as e:
        if "Private video" in str(e):
            await update.message.reply_text("❌ الفيديو خاص ولا يمكن تحميله")
        elif "Members only" in str(e):
            await update.message.reply_text("❌ الفيديو للأعضاء فقط")
        elif "Sign in" in str(e):
            await update.message.reply_text("❌ الفيديو يتطلب تسجيل دخول")
        else:
            await update.message.reply_text(f"❌ خطأ في التحميل: {str(e)}")
    
    except Exception as e:
        await update.message.reply_text(f"❌ صار خطأ غير متوقع: {str(e)}")

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ حتى تقدر تستخدم البوت، اشترك أولًا بالقناة: {CHANNEL_USERNAME}"
        )
        return

    url = update.message.text
    await handle_download(update, url)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("download", download_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))

print("🚀 البوت يشتغل...")
app.run_polling()
