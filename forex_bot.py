import telebot
import base64
import os
from openai import OpenAI
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توکن‌ها از Environment Variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # حالا مستقیم از نام استاندارد می‌خونه

# اتصال به AvalAI (بدون نیاز به api_key در کد — خودش از env var می‌گیره)
client = OpenAI(
    base_url="https://api.avalai.ir/v1"
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# پیام شروع
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("راهنما 📚", callback_data="help"))
    markup.add(InlineKeyboardButton("کانال سیگنال 🚀", url="https://t.me/+LINK_KANALE_SHOMA"))
    bot.send_message(message.chat.id,
                     "سلام به بات تحلیل چارت فارکس با هوش مصنوعی GPT-4o Vision 🔥\n"
                     "عکس چارت از TradingView یا MT4 بفرست تا تحلیل حرفه‌ای بدم!\n"
                     "یا نماد + تایم‌فریم بنویس (ولی عکس خیلی دقیق‌تره)",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         "راهنما:\n"
                         "• اسکرین‌شات چارت رو بفرست (بهترین نتیجه)\n"
                         "• یا نماد + تایم‌فریم بنویس\n"
                         "تحلیل شامل: روند، سطوح، الگوها، اندیکاتورها، سیگنال + استاپ/تارگت")

# تحلیل عکس چارت
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "چارت دریافت شد... در حال تحلیل حرفه‌ای ⏳")
    file_info = bot.get_file(message.photo[-1].file_id)
    photo_bytes = bot.download_file(file_info.file_path)
    base64_image = base64.b64encode(photo_bytes).decode('utf-8')
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                {"type": "text", "text": """تحلیل تکنیکال کامل و دقیق این چارت را به فارسی ساده و حرفه‌ای بده:
• روند کلی (صعودی / نزولی / رنج) + دلیل
• سطوح حمایت و مقاومت کلیدی (قیمت دقیق)
• وضعیت اندیکاتورها (RSI, MACD, Volume, MA)
• الگوهای کندلی یا چارتی
• سیگنال خرید یا فروش فعلی + احتمال تقریبی
• استاپ لاس و تارگت‌های ۱-۲-۳
• سناریوهای کوتاه و میان‌مدت
فقط تحلیل بده، بدون مقدمه یا نصیحت."""}
            ]
        }],
        max_tokens=1000
    )
    bot.reply_to(message, response.choices[0].message.content)

# اگر فقط متن فرستاد
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if len(message.text) < 80:
        bot.reply_to(message, "برای تحلیل دقیق، لطفاً عکس چارت رو بفرست! 📸\nتحلیل متنی فقط کلیات می‌گه.")
    else:
        bot.reply_to(message, "در حال پردازش...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message.text}],
            max_tokens=800
        )
        bot.reply_to(message, response.choices[0].message.content)

print("بات زنده شد!")
bot.polling(none_stop=True)
