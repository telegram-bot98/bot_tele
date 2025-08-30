import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re

TOKEN = "8197996560:AAFshyi0AYVcVULxwAANzNBz9RM7-9Y9kHc"
CHANNEL_USERNAME = "@p_y_hy"  # غير هذا إلى معرف قناتك

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ حتى تقدر تستخدم البوت، اشترك أولاً بالقناة: {CHANNEL_USERNAME}\n"
            f"بعد الاشتراك، أرسل /start مرة أخرى"
        )
        return

    await update.message.reply_text("""
🎬 أهلاً بك في بوت تحميل الفيديوهات!

📥 أرسل لي رابط من:
• تيك توك ✅
• انستقرام ✅ 
• تويتر ✅
• فيسبوك ✅

⚡ المميزات:
- تحميل سريع وجودة عالية
- دعم جميع المنصات
- حماية حقوق المحتوى

❌ اليوتيوب متوقف حالياً
""")

async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من اشتراك المستخدم في القناة"""
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك: {e}")
        return False

def download_tiktok(url):
    """تحميل من تيك توك"""
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            video_url = data['data']['play']
            
            # تحميل الفيديو
            video_response = requests.get(video_url, timeout=30)
            filename = "downloads/tiktok_video.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_response.content)
            
            return filename, None
        else:
            return None, "فشل في تحميل الفيديو من تيك توك"
            
    except Exception as e:
        return None, f"خطأ في تيك توك: {str(e)}"

def download_instagram(url):
    """تحميل من انستقرام"""
    try:
        # استخدام API مجاني لانستقرام
        api_url = f"https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"
        querystring = {"url": url}
        
        headers = {
            "X-RapidAPI-Key": "rapidapi_key_here",  # سجل في rapidapi.com واحصل على مفتاح
            "X-RapidAPI-Host": "instagram-downloader-download-instagram-videos-stories.p.rapidapi.com"
        }
        
        response = requests.get(api_url, headers=headers, params=querystring, timeout=30)
        data = response.json()
        
        if 'media' in data:
            video_url = data['media']
            
            video_response = requests.get(video_url, timeout=30)
            filename = "downloads/instagram_video.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_response.content)
            
            return filename, None
        else:
            return None, "فشل في تحميل من انستقرام"
            
    except Exception as e:
        return None, f"خطأ في انستقرام: {str(e)}"

def download_twitter(url):
    """تحميل من تويتر"""
    try:
        api_url = f"https://twitsave.com/info?url={url}"
        response = requests.get(api_url, timeout=30)
        
        # البحث عن رابط التحميل في الصفحة
        video_url_match = re.search(r'https://[^"]*\.mp4', response.text)
        
        if video_url_match:
            video_url = video_url_match.group(0)
            
            video_response = requests.get(video_url, timeout=30)
            filename = "downloads/twitter_video.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_response.content)
            
            return filename, None
        else:
            return None, "لم يتم العثور على فيديو في التغريدة"
            
    except Exception as e:
        return None, f"خطأ في تويتر: {str(e)}"

def download_facebook(url):
    """تحميل من فيسبوك"""
    try:
        api_url = f"https://getmyfb.com/process"
        payload = {
            'id': url,
            'locale': 'en'
        }
        
        response = requests.post(api_url, data=payload, timeout=30)
        
        # البحث عن رابط التحميل
        video_url_match = re.search(r'https://[^"]*\.mp4', response.text)
        
        if video_url_match:
            video_url = video_url_match.group(0)
            
            video_response = requests.get(video_url, timeout=30)
            filename = "downloads/facebook_video.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_response.content)
            
            return filename, None
        else:
            return None, "فشل في تحميل من فيسبوك"
            
    except Exception as e:
        return None, f"خطأ في فيسبوك: {str(e)}"

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التحقق من الاشتراك أولاً
    if not await is_subscribed(update, context):
        await update.message.reply_text(
            f"⚠️ حتى تقدر تستخدم البوت، اشترك أولاً بالقناة: {CHANNEL_USERNAME}\n"
            f"بعد الاشتراك، أرسل الرابط مرة أخرى"
        )
        return

    url = update.message.text.strip()
    
    # إضافة حقوقك إلى الرسالة
    copyright_notice = "\n\n⚡ بواسطة @AHMED_KHANA - جميع الحقوق محفوظة"
    
    await update.message.reply_text("🔍 جاري معالجة الرابط...")

    try:
        filename = None
        error = None
        
        # تحديد نوع المنصة
        if "tiktok.com" in url or "vm.tiktok.com" in url:
            await update.message.reply_text("📱 جاري تحميل من تيك توك...")
            filename, error = download_tiktok(url)
            
        elif "instagram.com" in url:
            await update.message.reply_text("📸 جاري تحميل من انستقرام...")
            filename, error = download_instagram(url)
            
        elif "twitter.com" in url or "x.com" in url:
            await update.message.reply_text("🐦 جاري تحميل من تويتر...")
            filename, error = download_twitter(url)
            
        elif "facebook.com" in url or "fb.com" in url:
            await update.message.reply_text("📘 جاري تحميل من فيسبوك...")
            filename, error = download_facebook(url)
            
        else:
            await update.message.reply_text("❌ هذا الرابط غير مدعوم أو غير صحيح")
            return

        if error:
            await update.message.reply_text(f"❌ {error}")
            return
            
        if filename and os.path.exists(filename):
            # التحقق من حجم الملف
            file_size = os.path.getsize(filename)
            if file_size > 50 * 1024 * 1024:  # 50MB حد تيليجرام
                await update.message.reply_text("❌ الملف كبير جداً للإرسال")
                os.remove(filename)
                return
                
            await update.message.reply_text("✅ تم التحميل! جاري الإرسال...")

            # إرسال الفيديو مع حقوقك
            with open(filename, "rb") as video:
                await update.message.reply_video(
                    video, 
                    caption=f"📥 تم التحميل بنجاح{copyright_notice}"
                )
            
            # حذف الملف بعد الإرسال
            os.remove(filename)
        else:
            await update.message.reply_text("❌ لم يتم إنشاء الملف، حاول برابط آخر")
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ غير متوقع: {str(e)}")

# إنشاء مجلد التحميلات
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# تشغيل البوت
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))

print("🚀 البوت يعمل مع ميزة التحقق من الاشتراك...")
app.run_polling()
