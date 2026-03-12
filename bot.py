import os
import logging
import base64
from collections import defaultdict
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import httpx

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

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

chat_histories = defaultdict(list)

# Matn uchun — gemini-2.0-flash (bepul ishlaydi)
GEMINI_CHAT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Rasm uchun — gemini-2.0-flash-exp (bepul, rasm ham qaytaradi)
GEMINI_IMAGE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"


def ask_gemini(user_id: int, user_message: str) -> str:
    chat_histories[user_id].append({
        "role": "user",
        "parts": [{"text": user_message}],
    })

    if len(chat_histories[user_id]) > MAX_HISTORY:
        chat_histories[user_id] = chat_histories[user_id][-MAX_HISTORY:]

    try:
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": chat_histories[user_id],
            "generationConfig": {
                "maxOutputTokens": 1024,
            },
        }

        with httpx.Client(timeout=60) as client:
            response = client.post(GEMINI_CHAT_URL, json=payload)
            data = response.json()

        if "error" in data:
            logger.error(f"Gemini xatosi: {data['error']}")
            return f"⚠️ Xatolik: {data['error'].get('message', 'Noma\'lum xato')}"

        text = data["candidates"][0]["content"]["parts"][0]["text"]

        chat_histories[user_id].append({
            "role": "model",
            "parts": [{"text": text}],
        })

        return text

    except Exception as e:
        logger.error(f"Gemini xatosi: {e}")
        return "⚠️ Kechirasiz, hozir javob bera olmayapman. Keyinroq urinib ko'ring."


def generate_image(prompt: str) -> tuple:
    try:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Generate a high quality image of: {prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
            },
        }

        with httpx.Client(timeout=120) as client:
            response = client.post(GEMINI_IMAGE_URL, json=payload)
            data = response.json()

        if "error" in data:
            logger.error(f"Rasm xatosi: {data['error']}")
            return None, f"⚠️ Xatolik: {data['error'].get('message', 'Noma\'lum xato')}"

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])

        for part in parts:
            if "inlineData" in part:
                image_bytes = base64.b64decode(part["inlineData"]["data"])
                return image_bytes, None

        for part in parts:
            if "text" in part:
                return None, f"❌ Rasm yaratilmadi: {part['text']}"

        return None, "❌ Rasm yaratib bo'lmadi. Boshqa tavsif bilan urinib ko'ring."

    except Exception as e:
        logger.error(f"Rasm yaratish xatosi: {e}")
        return None, "⚠️ Rasm yaratishda xatolik. Keyinroq urinib ko'ring."


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_histories[user.id] = []
    welcome = (
        f"Salom, {user.first_name}! 👋\n\n"
        f"Men **{BOT_NAME}**man — Gemini AI asosida ishlaydigan aqlli yordamchi.\n\n"
        "🧠 **Savol berish** — oddiy matn yozing\n"
        "🎨 **Rasm yaratish** — /image buyrug'ini ishlating\n\n"
        "**Misol:**\n"
        "`/image Tog'lar orasida quyosh botishi`\n"
        "`/image Koinotda suzayotgan astronavt`\n\n"
        "📋 **Buyruqlar:**\n"
        "/start — Yangi suhbat boshlash\n"
        "/image — Rasm yaratish\n"
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
        "🧠 **Savol berish** — oddiy matn yozing\n"
        "🎨 **Rasm yaratish** — `/image tavsif`\n\n"
        "**Misol:**\n"
        "`/image Bahorgi gullagan bog'`\n\n"
        "**Buyruqlar:**\n"
        "/start — Yangi suhbat\n"
        "/image — Rasm yaratish\n"
        "/clear — Tarixni tozalash\n"
        "/help — Yordam\n\n"
        "💡 **Maslahatlar:**\n"
        "• Savolni aniq yozing\n"
        "• Men oldingi xabarlarni eslayman\n"
        "• Rasm uchun batafsil tavsif yozing"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def cmd_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args) if context.args else ""

    if not prompt:
        await update.message.reply_text(
            "🎨 Rasm tavsifini yozing!\n\n"
            "**Misol:**\n"
            "`/image Tog'lar orasida quyosh botishi`\n"
            "`/image Kosmosda suzayotgan mushuk`",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        f"🎨 Rasm yaratilmoqda: *{prompt}*\n⏳ Iltimos, kuting...",
        parse_mode="Markdown"
    )
    await update.message.chat.send_action("upload_photo")

    image_bytes, error = generate_image(prompt)

    if image_bytes:
        from io import BytesIO
        photo = BytesIO(image_bytes)
        photo.name = "generated_image.png"
        await update.message.reply_photo(
            photo=photo,
            caption=f"🎨 *{prompt}*",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(error)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if not user_message or not user_message.strip():
        return

    user_id = update.effective_user.id
    logger.info(f"[{update.effective_user.first_name}]: {user_message[:80]}")

    await update.message.chat.send_action("typing")
    reply = ask_gemini(user_id, user_message)

    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await update.message.reply_text(reply[i:i + 4000])
    else:
        await update.message.reply_text(reply)


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Yangi suhbat boshlash"),
        BotCommand("image", "Rasm yaratish"),
        BotCommand("clear", "Tarixni tozalash"),
        BotCommand("help", "Yordam"),
    ])


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Xato: {context.error}")


def main():
    print("🤖 Bot ishga tushmoqda...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("image", cmd_image))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    print("✅ Bot tayyor!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
