import telebot
import base64
from openai import OpenAI
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توکن‌ها رو بعداً تو Environment Variables می‌ذاریم
TELEGRAM_TOKEN = '8297444523:AAGB4xlzBxOJ4xCFt26khzRsNeMCmebkNVc'  # فقط برای تست محلی
AVALAI_API_KEY = 'aa-T3FzjWoZXlBTytippDrTIgGla1gaCoYXtKtIdM1uVJk2wCmU'  # فقط برای تست محلی

client = OpenAI(
    api_key=AVALAI_API_KEY,
    base_url="https://api.avalai.ir/v1"
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# بقیه کد دقیقاً همون قبلیه
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("راهنما 📚", callback_data="help"))
    markup.add(InlineKeyboardButton("کانال سیگنال 🚀", url="https://t.me/+YOUR_CHANNEL_LINK"))
    bot.send_message(message.chat.id,
                     "سلام به بات تحلیل چارت فارکس با هوش مصنوعی GPT-4o 🔥\n"
                     "عکس چارت بفرست یا نماد + تایم‌فریم بنویس (مثل EURUSD H4)\n"
                     "تحلیل حرفه‌ای + سیگنال می‌دم!",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "راهنما:\n• عکس چارت بفرست\n• یا نماد بنویس\nتحلیل کامل می‌دم")

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
                {"type": "text", "text": """این یک چارت فارکس یا کریپتو است. تحلیل تکنیکال کامل و حرفه‌ای به فارسی ساده بده:
- روند کلی
- سطوح حمایت/مقاومت کلیدی
- الگوهای کندلی یا چارتی
- وضعیت RSI, MACD, MA
- سیگنال خرید/فروش با احتمال
- استاپ لاس و تارگت پیشنهادی
فقط تحلیل بده، بدون مقدمه طولانی."""}
            ]
        }],
        max_tokens=800
    )
    bot.reply_to(message, response.choices[0].message.content)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if len(message.text) < 50:
        bot.reply_to(message, "در حال تحلیل نماد... ⏳")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"تحلیل تکنیکال کامل نماد {message.text} در تایم‌فریم‌های روزانه و ۴ ساعته به فارسی ساده: روند، سطوح، اندیکاتورها، سیگنال و مدیریت ریسک."}],
            max_tokens=800
        )
        bot.reply_to(message, response.choices[0].message.content)

print("بات در حال اجراست...")
bot.polling()
