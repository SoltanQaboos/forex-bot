import telebot
import base64
import os
from openai import OpenAI
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توکن‌ها
TELEGRAM_TOKEN = os.getenv('8297444523:AAGB4xlzBxOJ4xCFt26khzRsNeMCmebkNVc')
OPENAI_API_KEY = os.getenv('aa-T3FzjWoZXlBTytippDrTIgGla1gaCoYXtKtIdM1uVJk2wCmU')

# اتصال به AvalAI - این نسخه با 1.35.10 کاملاً کار می‌کنه
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.avalai.ir/v1"
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# شروع
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("راهنما 📚", callback_data="help"))
    markup.add(InlineKeyboardButton("کانال سیگنال 🚀", url="https://t.me/+LINK_KANALE_SHOMA"))
    bot.send_message(message.chat.id,
                     "سلام! بات تحلیل چارت فارکس با GPT-4o Vision 🔥\n"
                     "عکس چارت بفرست تا تحلیل حرفه‌ای بدم!",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "فقط عکس چارت بفرست، تحلیل دقیق می‌دم!")

# تحلیل عکس
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "در حال تحلیل چارت... ⏳")
    file_info = bot.get_file(message.photo[-1].file_id)
    photo_bytes = bot.download_file(file_info.file_path)
    base64_image = base64.b64encode(photo_bytes).decode('utf-8')
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                {"type": "text", "text": """تحلیل تکنیکال کامل این چارت رو به فارسی بده:
• روند کلی + دلیل
• سطوح حمایت/مقاومت دقیق
• وضعیت اندیکاتورها
• الگوها
• سیگنال خرید/فروش + احتمال
• استاپ و تارگت
• سناریو کوتاه/میان‌مدت
فقط تحلیل، بدون مقدمه.""")}
            ]
        }],
        max_tokens=1000
    )
    bot.reply_to(message, response.choices[0].message.content)

# متن ساده
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.reply_to(message, "عکس چارت بفرست تا تحلیل دقیق بدم! 📸")

print("بات زنده شد!")
bot.polling(none_stop=True)
