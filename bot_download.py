import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re

TOKEN = "8197996560:AAFshyi0AYVcVULxwAANzNBz9RM7-9Y9kHc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 **أهلاً! أنا بوت احمد خان لتحميل الفيديوهات**\n\n"
                                  "📥 **أرسل لي رابط فيديو من:**\n"
                                  "• يوتيوب 📺\n"
                                  "• إنستغرام 📸\n"
                                  "• تيك توك 🎵\n" 
                                  "• تويتر 🐦\n"
                                  "• فيسبوك 👍\n\n"
                                  "⚡ **وسأحمله لك فوراً!**")

def is_youtube_url(url):
    """يتحقق إذا كان الرابط من يوتيوب"""
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube|youtu)\.(com|be)',
        r'youtube\.com/watch\?v=',
        r'youtu\.be/'
    ]
    return any(re.search(pattern, url) for pattern in youtube_patterns)

def download_video(url):
    """دالة التحميل الذكية"""
    ydl_opts = {
        'format': 'best[filesize<50M]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        'retries': 3,
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls', 'thumbnails'],
            }
        },
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    
    # إذا كان رابط يوتيوب، أضف خيارات إضافية
    if is_youtube_url(url):
        ydl_opts.update({
            'extract_flat': False,
            'ignoreerrors': True,
            'no_check_certificate': True,
        })
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # تأكد أن الملف موجود
            if os.path.exists(filename):
                return filename
            else:
                raise Exception("الملف لم يتم إنشاؤه")
                
        except Exception as e:
            # المحاولة بطريقة بديلة لليوتيوب
            if is_youtube_url(url):
                try:
                    ydl_opts_alt = {
                        'format': 'best[height<=720]',
                        'outtmpl': 'downloads/%(title)s.%(ext)s',
                        'quiet': True,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts_alt) as ydl_alt:
                        info = ydl_alt.extract_info(url, download=True)
                        return ydl_alt.prepare_filename(info)
                except:
                    raise Exception("فيديو اليوتيوب يحتاج تحقق. جرب فيديو آخر")
            raise Exception(f"خطأ في التحميل: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = update.message.text.strip()
        
        if not url.startswith(('http://', 'https://')):
            await update.message.reply_text("❌ **أرسل رابط صحيح يبدأ بـ http:// أو https://**")
            return
            
        await update.message.reply_text("⏳ **جاري التحميل...**")
        
        filename = download_video(url)
        await update.message.reply_text("✅ **تم التحميل! جاري الإرسال...**")

        # أرسل الفيديو مع معالجة الأخطاء
        try:
            with open(filename, "rb") as video:
                await update.message.reply_video(
                    video, 
                    caption="📥 تم التحميل بنجاح",
                    supports_streaming=True,
                    timeout=300
                )
        except Exception as send_error:
            await update.message.reply_text("📨 **حجم الفيديو كبير جداً**\n\n"
                                          "📋 **جرب:**\n"
                                          "• فيديو أقصر\n"
                                          "• رابط من إنستغرام/تيك توك\n"
                                          f"❌ {str(send_error)}")

        # تنظيف الملف
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass
            
        await update.message.reply_text("🎉 **تم بنجاح! أرسل رابط آخر**")
        
    except Exception as e:
        error_msg = str(e)
        
        if "تحقق" in error_msg or "Sign in" in error_msg or "cookies" in error_msg:
            await update.message.reply_text("⚠️ **لم أستطع تحميل فيديو اليوتيوب**\n\n"
                                          "🎯 **الحلول:**\n"
                                          "• جرب فيديو من إنستغرام أو تيك توك\n"
                                          "• جرب فيديو يوتيوب مختلف\n"
                                          "• بعض الفيديوهات تحتاج تحقق\n\n"
                                          "📸 **إنستغرام وتيك توك يعملان دائماً!**")
        else:
            await update.message.reply_text(f"❌ **خطأ:** {error_msg}")

# الإعدادات
if not os.path.exists("downloads"):
    os.makedirs("downloads")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 البوت يعمل...")
app.run_polling()
