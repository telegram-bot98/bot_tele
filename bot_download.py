import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import requests
from urllib.parse import quote

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8197996560:AAFshyi0AYVcVULxwAANzNBz9RM7-9Y9kHc"
CHANNEL_USERNAME = "@p_y_hy"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ **يجب أن تشترك في قناتي أولاً:**\n{CHANNEL_USERNAME}\n\n"
            "بعد الاشتراك، أرسل /start مرة أخرى"
        )
        return
        
    await update.message.reply_text(
        "🎬 **أهلاً! أنا بوت احمد خان لتحميل الفيديوهات**\n\n"
        "🔍 **يمكنك:**\n"
        "• إرسال رابط فيديو للتحميل\n"
        "• استخدام /search + كلمة للبحث في اليوتيوب\n\n"
        "📥 **المنصات المدعومة:**\n"
        "• إنستغرام 📸 • تيك توك 🎵 • فيسبوك 👍\n"
        "• تويتر 🐦 • يوتيوب 📺 • وغيرها\n\n"
        "⚡ **أرسل رابط أو ابحث الآن!**"
    )

async def search_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بحث في اليوتيوب"""
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ **يجب أن تشترك في قناتي أولاً:**\n{CHANNEL_USERNAME}\n\n"
            "بعد الاشتراك، أرسل /search مرة أخرى"
        )
        return

    if not context.args:
        await update.message.reply_text("❌ **أكتب ما تريد البحث عنه:**\n`/search أغنية جديدة`")
        return

    search_query = " ".join(context.args)
    await update.message.reply_text(f"🔍 **جاري البحث عن:** {search_query}")

    try:
        # البحث في اليوتيوب
        results = search_youtube_videos(search_query)
        
        if not results:
            await update.message.reply_text("❌ **لم أجد نتائج للبحث**")
            return

        # إرسال النتائج
        message = "📺 **نتائج البحث في اليوتيوب:**\n\n"
        for i, result in enumerate(results[:5], 1):  # أول 5 نتائج
            message += f"{i}. [{result['title']}]({result['url']})\n"
            message += f"   ⏰ {result['duration']} | 👁️ {result['views']}\n\n"

        message += "📥 **أرسل الرابط لتحميل الفيديو**"
        
        await update.message.reply_text(
            message, 
            parse_mode='Markdown',
            disable_web_page_preview=False
        )

    except Exception as e:
        await update.message.reply_text(f"❌ **حدث خطأ في البحث:** {str(e)}")

def search_youtube_videos(query, max_results=5):
    """بحث عن فيديوهات في اليوتيوب"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'force_json': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # البحث في اليوتيوب
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            
            if not info or 'entries' not in info:
                return []

            results = []
            for entry in info['entries']:
                if entry:  # التأكد من وجود البيانات
                    results.append({
                        'title': entry.get('title', 'بدون عنوان'),
                        'url': entry.get('url', ''),
                        'duration': entry.get('duration', 'غير معروف'),
                        'views': entry.get('view_count', 'غير معروف'),
                        'channel': entry.get('uploader', 'غير معروف')
                    })
            
            return results

    except Exception as e:
        logging.error(f"خطأ في البحث: {e}")
        return []

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التعامل مع طلبات التحميل"""
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ **يجب أن تشترك في قناتي أولاً:**\n{CHANNEL_USERNAME}\n\n"
            "بعد الاشتراك، أرسل الرابط للتحميل"
        )
        return

    url = update.message.text.strip()
    
    # إذا كان بحثاً وليس رابطاً
    if url.startswith('/search'):
        await search_youtube(update, context)
        return
        
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text(
            "❌ **هذا ليس رابطاً صالحاً**\n\n"
            "🔍 **جرب:**\n"
            "• إرسال رابط فيديو مباشر\n"
            "• استخدام /search للبحث في اليوتيوب"
        )
        return

    await update.message.reply_text("⏳ جاري التحميل، انتظر قليلاً...")

    try:
        filename = download_video(url)
        await update.message.reply_text("✅ تم التحميل! جاري الإرسال...")

        with open(filename, "rb") as video:
            await update.message.reply_video(
                video,
                caption="📥 تم التحميل بنجاح\n\n" +
                       f"👉 تابعني على {CHANNEL_USERNAME} للمزيد",
                supports_streaming=True
            )

        if os.path.exists(filename):
            os.remove(filename)
            
        await update.message.reply_text("🎉 تم الانتهاء! أرسل رابط آخر")
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

def download_video(url):
    """دالة التحميل"""
    ydl_opts = {
        'format': 'best[filesize<50M]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        'retries': 2,
        'merge_output_format': 'mp4',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من الاشتراك"""
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"خطأ في التحقق: {e}")
        return False

def main():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    app = Application.builder().token(TOKEN).build()
    
    # إضافة handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search_youtube))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))

    logging.info("🚀 بدأ تشغيل البوت مع ميزة البحث...")
    app.run_polling()

if __name__ == "__main__":
    main()
