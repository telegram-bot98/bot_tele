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

TOKEN = "8197996560:AAFshyi0AYVcVULxwAANzNBz9RM7-9Y9kHc"
CHANNEL_USERNAME = "@p_y_hy"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يرحب بالمستخدم"""
    await update.message.reply_text(
        "🎬 **أهلاً! أنا بوت احمد خان لتحميل الفيديوهات**\n\n"
        "📥 **أرسل لي رابط فيديو من:**\n"
        "• يوتيوب 📺\n• إنستغرام 📸\n• تيك توك 🎵\n"
        "⚡ **وسأحمله لك فوراً!**"
    )

async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يتحقق من اشتراك المستخدم في القناة"""
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"خطأ في التحقق من الاشتراك: {e}")
        return False

def download_video(url):
    """دالة التحميل المحسنة"""
    ydl_opts = {
        'format': 'best[filesize<50M]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        'retries': 3,
        'merge_output_format': 'mp4',
        
        # إعدادات خاصة للمنصات المختلفة
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'format': 'best[height<=720]'
            },
            'instagram': {
                'format': 'best'
            },
            'tiktok': {
                'format': 'best'
            }
        },
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if os.path.exists(filename):
                return filename
            else:
                raise Exception("الملف لم يتم إنشاؤه")
                
        except Exception as e:
            # المحاولة بطريقة أبسط
            try:
                simple_opts = {
                    'format': 'best',
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'quiet': True,
                }
                with yt_dlp.YoutubeDL(simple_opts) as ydl_simple:
                    info = ydl_simple.extract_info(url, download=True)
                    return ydl_simple.prepare_filename(info)
            except:
                raise Exception(f"فشل التحميل: {str(e)}")

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يتعامل مع طلبات التحميل"""
    # التحقق من الاشتراك أولاً
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ يرجى الاشتراك في القناة أولاً:\n{CHANNEL_USERNAME}\n\n"
            "بعد الاشتراك، أرسل /start مرة أخرى"
        )
        return

    url = update.message.text.strip()
    
    # التحقق من صحة الرابط
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ هذا ليس رابطاً صالحاً")
        return

    await update.message.reply_text("⏳ جاري التحميل، انتظر قليلاً...")

    try:
        filename = download_video(url)
        await update.message.reply_text("✅ تم التحميل! جاري الإرسال...")

        # إرسال الفيديو
        with open(filename, "rb") as video:
            await update.message.reply_video(
                video,
                caption="📥 تم التحميل بنجاح",
                supports_streaming=True
            )

        # تنظيف الملف
        if os.path.exists(filename):
            os.remove(filename)
            
        await update.message.reply_text("🎉 تم الانتهاء! يمكنك إرسال رابط آخر")
        
    except Exception as e:
        error_msg = str(e)
        if "Sign in" in error_msg or "cookies" in error_msg:
            await update.message.reply_text(
                "⚠️ لم أستطع تحميل هذا الفيديو\n\n"
                "📌 جرب روابط من:\n• إنستغرام\n• تيك توك\n• تويتر\n\n"
                "🎬 هذه المنصات تعمل بشكل أفضل!"
            )
        else:
            await update.message.reply_text(f"❌ حدث خطأ: {error_msg}")

def main():
    """الدالة الرئيسية"""
    # إنشاء مجلد التحميلات
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    # التحقق من التوكن
    if not TOKEN or TOKEN == "ضع_توكن_بوتك_هنا":
        logging.error("❌ لم تقم بوضع توكن البوت!")
        return

    # إنشاء وتشغيل البوت
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))

    logging.info("🚀 بدأ تشغيل البوت...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
