from telegram import Bot

TELEGRAM_TOKEN = "8936438800:AAF0TyJ7A2lZk1Tq0BQXYBplqACPHKCwNOM"
CHAT_ID = "6002099959"

# Test sending a message
bot = Bot(token=TELEGRAM_TOKEN)
bot.send_message(chat_id=CHAT_ID, text="🟢 Test message! Your bot is working!")
print("✅ Test message sent! Check your Telegram.")