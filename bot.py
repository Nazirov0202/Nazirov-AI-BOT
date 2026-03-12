import os
import logging
from collections import defaultdict
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import anthropic

# Kalitlar Railway muhit o'zgaruvchilaridan olinadi
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]

BOT_NAME = "AI Yordamchi"
MAX_HISTORY = 20

SYSTEM_PROMPT = f"""Sen aqlli va do'stona AI yordamchisan. Sening isming "{BOT_NAME}".

Vazifang:
- Foydalanuvchilarning savollariga aniq va foydali javob berish
- O'zbek va ingliz tillarida suhbatlashish
- Murakkab mavzularni oddiy tushuntirish
- Doimo xushmuomala va hurmatli bo'lish
- Kod yozishda yordam berish
- Tarjima qilish

Javoblaringni Telegram formatida yoz:
- Qisqa va aniq bo'l (1-3 paragraf)
- Emoji ishlatishing mumkin
- Kod uchun ``` belgisini ishlat
- Muhim so'zlarni **qalin** qil
"""

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
chat_histories = defaultdict(list)


def ask_claude(user_id: int, user_message: str) -> str:
    chat_histories[user_id].append({"role": "user", "content": user_message})

    if len(chat_histories[user_id]) > MAX_HISTORY:
        chat_histories[user_id] = chat_histories[user_id][-MAX_HISTORY:]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=chat_histories[user_id],
        )
        assistant_message = response.content[0].text
        chat_histories[user_id].append({"role": "assistant", "content": assistant_message})
        return assistant_message

    except anthropic.AuthenticationError:
        return "🔑 Claude API kaliti noto'g'ri. Railway sozlamalarini tekshiring."
    except anthropic.RateLimitError:
        return "⏳ So'rovlar limiti tugadi. Bir oz kutib, qayta urinib ko'ring."
    except anthropic.APIError as e:
        logger.error(f"Claude API xatosi: {e}")
        return "⚠️ Kechirasiz, hozir javob bera olmayapman. Keyinroq urinib ko'ring."
    except Exception as e:
        logger.error(f"Kutilmagan xato: {e}")
        return "❌ Xatolik yuz berdi. /start bosing va qayta urinib ko'ring."


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_histories[user.id] = []
    welcome = (
        f"Salom, {user.first_name}! 👋\n\n"
        f"Men **{BOT_NAME}**man — Claude AI asosida ishlaydigan aqlli yordamchi.\n\n"
        "🧠 Menga istalgan savolingizni yozing:\n"
        "• Dasturlash, matematika, fan\n"
        "• Tarjima qilish\n"
        "• Maslahat va g'oyalar\n"
        "• Matn yozish va tahlil qilish\n\n"
        "📋 **Buyruqlar:**\n"
        "/start — Yangi suhbat boshlash\n"
        "/clear — Suhbat tarixini tozalash\n"
        "/help — Yordam\n\n"
        "Menga yozing! ✨"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories[update.effective_user.id] = []
    await update.message.reply_text("🧹 Suhbat tarixi tozalandi! Yangi mavzuda gaplashishimiz mumkin.")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🔍 **Yordam**\n\n"
        "Oddiy matn yozing — men javob beraman!\n\n"
        "**Buyruqlar:**\n"
        "/start — Yangi suhbat\n"
        "/clear — Tarixni tozalash\n"
        "/help — Yordam\n\n"
        "💡 **Maslahatlar:**\n"
        "• Savolni aniq yozing\n"
        "• Men oldingi xabarlarni eslayman\n"
        "• Yangi mavzu uchun /clear bosing"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if not user_message or not user_message.strip():
        return

    user_id = update.effective_user.id
    logger.info(f"[{update.effective_user.first_name}]: {user_message[:80]}")

    await update.message.chat.send_action("typing")
    reply = ask_claude(user_id, user_message)

    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await update.message.reply_text(reply[i:i + 4000])
    else:
        await update.message.reply_text(reply)


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Yangi suhbat boshlash"),
        BotCommand("clear", "Tarixni tozalash"),
        BotCommand("help", "Yordam"),
    ])


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Xato: {context.error}")


def main():
    print("🤖 Bot ishga tushmoqda...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    print("✅ Bot tayyor!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
