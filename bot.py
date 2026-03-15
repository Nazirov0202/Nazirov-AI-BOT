import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "BU_YERGA_TOKEN_QOYING")
GROUP_CHAT_ID = -1003809622723

NUM_EMOJI = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

QUESTIONS_LOTIN = [
    "Siz qaysi dastgohda ishlaysiz?\n(Masalan: Pechat, Tigel, Laminatsiya, Gofra liniya, Kashirovka, Ombor)",
    "Sizning dastgohingizdan qaysi mahsulotlar o'tadi?\n(Masalan: Indorama, Belissimo)",
    "Shu mahsulotlar sizning dastgohingizdan o'tganda qanday muammolar yuzaga keladi? Barchasini yozing.\n(Masalan: rang farq qiladi, o'lcham noto'g'ri chiqadi)",
    "Bu muammolardan qaysi biri eng ko'p takrorlanadi va ishni to'xtatadi?\n(Masalan: har kuni / haftada bir necha marta)",
    "Muammo yuzaga kelganda mahsulotga nima bo'ladi?\n(Masalan: qayta ishlanadi, yo'q qilinadi, keyingi bosqichga o'tadi)",
    "Bu muammolarning asosiy sababi nima deb o'ylaysiz?\n(Masalan: dastgoh eski, material sifatsiz, sozlash noto'g'ri)",
    "Bu muammolar tufayli qancha mahsulot isrof bo'ladi?\n(Masalan: 1 oyda nechta mahsulot)",
    "Bu muammolarni hal qilish uchun nima qildingiz? Natija bo'ldimi?\n(Masalan: texnologga aytdim, sozladim, lekin yana takrorlandi)",
    "Muammoni butunlay yo'qotish uchun nima kerak deb o'ylaysiz?\n(Masalan: dastgohni ta'mirlash, yangi material, qo'shimcha o'qitish)",
    "Dastgohingiz va ish joyingizni yaxshilash uchun yana qanday taklifingiz bor?",
]

QUESTIONS_KIRILL = [
    "Сиз қайси дастгоҳда ишлайсиз?\n(Масалан: Печат, Тигель, Ламинация, Гофра линия, Кашировка, Омбор)",
    "Сизнинг дастгоҳингиздан қайси маҳсулотлар ўтади?\n(Масалан: Индорама, Белиссимо)",
    "Шу маҳсулотлар сизнинг дастгоҳингиздан ўтганда қандай муаммолар юзага келади? Барчасини ёзинг.\n(Масалан: ранг фарқ қилади, ўлчам нотўғри чиқади)",
    "Бу муаммолардан қайси бири энг кўп такрорланади ва ишни тўхтатади?\n(Масалан: ҳар куни / ҳафтада бир неча марта)",
    "Муаммо юзага келганда маҳсулотга нима бўлади?\n(Масалан: қайта ишланади, йўқ қилинади, кейинги босқичга ўтади)",
    "Бу муаммоларнинг асосий сабаби нима деб ўйлайсиз?\n(Масалан: дастгоҳ эски, материал сифатсиз, созлаш нотўғри)",
    "Бу муаммолар туфайли қанча маҳсулот исроф бўлади?\n(Масалан: 1 ойда нечта маҳсулот)",
    "Бу муаммоларни ҳал қилиш учун нима қилдингиз? Натижа бўлдими?\n(Масалан: технологга айтдим, созладим, лекин яна такрорланди)",
    "Муаммони бутунлай йўқотиш учун нима керак деб ўйлайсиз?\n(Масалан: дастгоҳни таъмирлаш, янги материал, қўшимча ўқитиш)",
    "Дастгоҳингиз ва иш жойингизни яхшилаш учун яна қандай таклифингиз бор?",
]

QUESTIONS_RU = [
    "На каком станке вы работаете?\n(Например: Печать, Тигель, Ламинация, Гофролиния, Кашировка, Склад)",
    "Какие продукты проходят через ваш станок?\n(Например: Indorama, Belissimo)",
    "Какие проблемы возникают с этими продуктами на вашем станке? Напишите все.\n(Например: различие в цвете, неправильный размер)",
    "Какая из этих проблем повторяется чаще всего и останавливает работу?\n(Например: каждый день / несколько раз в неделю)",
    "Что происходит с продуктом при возникновении проблемы?\n(Например: переделывается, выбрасывается, переходит на следующий этап)",
    "По вашему мнению, в чём основная причина этих проблем?\n(Например: станок старый, материал некачественный, неправильная настройка)",
    "Сколько продукции теряется из-за этих проблем?\n(Например: сколько штук в месяц)",
    "Что вы сделали для решения этих проблем? Был ли результат?\n(Например: сказал технологу, настроил, но проблема повторилась)",
    "Что нужно, чтобы полностью устранить проблему?\n(Например: ремонт станка, новый материал, дополнительное обучение)",
    "Какие ещё предложения у вас есть по улучшению вашего станка и рабочего места?",
]

# Eslatma xabarlari
REMINDER_LOTIN = "⚠️ Eslatma!! Barcha ma'lumotlar sir saqlanadi.\nVaqtingizni ajratganingiz uchun tashakkur."
REMINDER_KIRILL = "⚠️ Эслатма!! Барча маълумотлар сир сақланади.\nВақтингизни ажратганингиз учун ташаккур."
REMINDER_RU = "⚠️ Напоминание!! Все данные хранятся в тайне.\nСпасибо за уделённое время."

CONTINUE_LOTIN = "🔄 Botni qaytadan ishga tushirib, siz ko'rgan boshqa mahsulotlardagi muammolarni ham yozishingiz mumkin. Takliflarni yozish cheksiz, so'rovnomada qancha ko'p ishtirok etsangiz shuncha ko'p bonus olasiz."
CONTINUE_KIRILL = "🔄 Ботни қайтадан ишга тушириб, сиз кўрган бошқа маҳсулотлардаги муаммоларни ҳам ёзишингиз мумкин. Таклифларни ёзиш чексиз, сўровномада қанча кўп иштирок этсангиз шунча кўп бонус оласиз."
CONTINUE_RU = "🔄 Вы можете перезапустить бота и написать о проблемах с другими продуктами, которые вы видели. Предложений можно писать сколько угодно — чем больше участвуете, тем больше бонусов получите."

# E'lon matni
ELON_TEXT = """📢 E'lon !!

So'rovnomada qatnashgan xodimlar taqdirlanadi.

🏆 1) So'rovnomani birinchi to'ldirgan 10 ta xodim — 100.000 so'm pul mukofoti bilan taqdirlanadi.

🏆 2) So'rovnomada eng ko'p muammo yozgan 10 ta xodim — 100.000 so'm pul mukofoti bilan taqdirlanadi.

🏆 3) So'rovnomani batafsil to'ldirgan 10 ta xodim — 100.000 so'm pul mukofoti bilan taqdirlanadi.

⛔️ So'rovnomada qatnashmagan xodimlarga 300.000 so'm jarima qo'llaniladi.

✅ 1 ta xodim uchchala yo'nalishda ham g'olib bo'lishi mumkin.

Hammangizdan so'rovnomada faol qatnashishni so'raymiz!"""

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

LANG, SCRIPT, DEPARTMENT, FULLNAME, SURVEY = range(5)


def get_questions(context):
    lang = context.user_data.get("lang")
    script = context.user_data.get("script")
    if lang == "ru":
        return QUESTIONS_RU
    elif script == "kirill":
        return QUESTIONS_KIRILL
    else:
        return QUESTIONS_LOTIN


async def delete_msg(context, chat_id, msg_id):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception:
        pass


async def clear_old_messages(context, chat_id):
    for mid in context.user_data.get("del", []):
        await delete_msg(context, chat_id, mid)
    context.user_data["del"] = []


async def post_init(application):
    description = (
        "👋 Assalomu alaykum!\n\n"
        "🏢 Europrint kompaniyasi xodimlar bilan "
        "savol-javob botiga xush kelibsiz!!\n\n"
        "Kompaniyamiz g'oyasi:\n\n"
        "Xodim va rahbarlarga bog'liq bo'lmagan, "
        "barcha jarayonlari to'liq avtomatlashtirilgan, "
        "aniq qoida va siyosatlari yozilgan, "
        "xodimlari hamda dastgohlari 101% "
        "samaradorlikka erishgan, "
        "mijozga 101% sifatga ega bo'lgan mahsulot "
        "taqdim etuvchi "
        "Markaziy Osiyodagi yetakchi tizimli kompaniya."
    )
    short_description = "🏢 Europrint kompaniyasi xodimlar savol-javob boti"

    try:
        await application.bot.set_my_description(description)
        await application.bot.set_my_short_description(short_description)
        await application.bot.set_my_commands([
            BotCommand("start", "So'rovnomani boshlash"),
            BotCommand("cancel", "Bekor qilish"),
        ])
    except Exception as e:
        logger.error(f"Bot sozlamalarida xatolik: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "del" in context.user_data:
        for mid in context.user_data.get("del", []):
            await delete_msg(context, update.message.chat_id, mid)

    context.user_data.clear()
    context.user_data["del"] = []

    # E'lonni yuborish
    elon_msg = await update.message.reply_text(ELON_TEXT)

    # Til tanlash tugmalari
    kb = [[
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="ru"),
    ]]

    msg = await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык:",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return LANG


async def lang_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer(cache_time=0)
    lang = q.data
    context.user_data["lang"] = lang


    if lang == "uz":
        kb = [[
            InlineKeyboardButton("🔤 Lotin", callback_data="lotin"),
            InlineKeyboardButton("🔡 Кирилл", callback_data="kirill"),
        ]]
        msg = await context.bot.send_message(
            chat_id=q.message.chat_id,
            text="📝 Yozuv turini tanlang:",
            reply_markup=InlineKeyboardMarkup(kb),
        )
        return SCRIPT
    else:
        context.user_data["script"] = "ru"
        kb = [
            [InlineKeyboardButton("Офсет", callback_data="dept_ofset"), InlineKeyboardButton("Флексо", callback_data="dept_flekso")],
            [InlineKeyboardButton("1-Департамент", callback_data="dept_1departament"), InlineKeyboardButton("2-Департамент", callback_data="dept_2departament")],
            [InlineKeyboardButton("4-Департамент", callback_data="dept_4departament"), InlineKeyboardButton("5-Департамент", callback_data="dept_5departament")],
        ]
        msg = await context.bot.send_message(
            chat_id=q.message.chat_id,
            text="🏭 Выберите ваш отдел:",
            reply_markup=InlineKeyboardMarkup(kb),
        )
        return DEPARTMENT


async def script_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer(cache_time=0)
    context.user_data["script"] = q.data


    if q.data == "kirill":
        kb = [
            [InlineKeyboardButton("Офсет", callback_data="dept_ofset"), InlineKeyboardButton("Флексо", callback_data="dept_flekso")],
            [InlineKeyboardButton("1-Департамент", callback_data="dept_1departament"), InlineKeyboardButton("2-Департамент", callback_data="dept_2departament")],
            [InlineKeyboardButton("4-Департамент", callback_data="dept_4departament"), InlineKeyboardButton("5-Департамент", callback_data="dept_5departament")],
        ]
        text = "🏭 Бўлимингизни танланг:"
    else:
        kb = [
            [InlineKeyboardButton("Ofset", callback_data="dept_ofset"), InlineKeyboardButton("Flekso", callback_data="dept_flekso")],
            [InlineKeyboardButton("1-Departament", callback_data="dept_1departament"), InlineKeyboardButton("2-Departament", callback_data="dept_2departament")],
            [InlineKeyboardButton("4-Departament", callback_data="dept_4departament"), InlineKeyboardButton("5-Departament", callback_data="dept_5departament")],
        ]
        text = "🏭 Bo'limingizni tanlang:"

    msg = await context.bot.send_message(
        chat_id=q.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return DEPARTMENT


async def dept_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer(cache_time=0)

    dept = q.data.replace("dept_", "")
    dept_map = {
        "ofset": "Ofset",
        "flekso": "Flekso",
        "1departament": "1-Departament",
        "2departament": "2-Departament",
        "4departament": "4-Departament",
        "5departament": "5-Departament",
    }
    context.user_data["department"] = dept_map.get(dept, dept)

    lang = context.user_data.get("lang")
    script = context.user_data.get("script")


    if lang == "ru":
        text = "👤 Напишите ваше имя и фамилию:"
    elif script == "kirill":
        text = "👤 Исм ва фамилиянгизни ёзинг:"
    else:
        text = "👤 Ism va familiyangizni yozing:"

    msg = await context.bot.send_message(chat_id=q.message.chat_id, text=text, )
    return FULLNAME


async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fullname"] = update.message.text
    context.user_data["answers"] = []
    context.user_data["q_num"] = 0

    return await send_question(update.message.chat_id, context)


async def send_question(chat_id, context):
    questions = get_questions(context)
    i = context.user_data["q_num"]
    lang = context.user_data.get("lang")
    script = context.user_data.get("script")

    if lang == "ru":
        label = "Опрос"
    elif script == "kirill":
        label = "Сўровнома"
    else:
        label = "So'rovnoma"

    num = NUM_EMOJI[i] if i < len(NUM_EMOJI) else f"{i+1}."
    header = f"📋 {label} ({i + 1}/{len(questions)})\n\n{num} "

    msg = await context.bot.send_message(chat_id=chat_id, text=header + questions[i], )
    return SURVEY


async def got_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = get_questions(context)
    context.user_data["answers"].append(update.message.text)
    context.user_data["q_num"] += 1

    if context.user_data["q_num"] >= len(questions):
        return await finish(update.message.chat_id, context)
    return await send_question(update.message.chat_id, context)


async def finish(chat_id, context):
    lang = context.user_data.get("lang")
    script = context.user_data.get("script")
    name = context.user_data["fullname"]
    dept = context.user_data["department"]
    answers = context.user_data["answers"]
    questions = get_questions(context)

    if lang == "ru":
        thanks = "✅ Спасибо! Опрос успешно завершён.\n\nВаши ответы приняты."
        reminder = REMINDER_RU
        continue_msg = CONTINUE_RU
        til = "🇷🇺 Русский"
    elif script == "kirill":
        thanks = "✅ Раҳмат! Сўровнома муваффақиятли якунланди.\n\nЖавобларингиз қабул қилинди."
        reminder = REMINDER_KIRILL
        continue_msg = CONTINUE_KIRILL
        til = "🇺🇿 Ўзбек (Кирилл)"
    else:
        thanks = "✅ Rahmat! So'rovnoma muvaffaqiyatli yakunlandi.\n\nJavoblaringiz qabul qilindi."
        reminder = REMINDER_LOTIN
        continue_msg = CONTINUE_LOTIN
        til = "🇺🇿 O'zbek (Lotin)"

    await context.bot.send_message(chat_id=chat_id, text=thanks + "\n\n" + reminder)

    if lang == "ru":
        btn_text = "🔄 Пройти ещё раз"
    elif script == "kirill":
        btn_text = "🔄 Яна иштирок этиш"
    else:
        btn_text = "🔄 Yana ishtirok etish"

    kb = [[InlineKeyboardButton(btn_text, callback_data="restart_survey")]]
    await context.bot.send_message(
        chat_id=chat_id,
        text=continue_msg,
        reply_markup=InlineKeyboardMarkup(kb)
    )

    text = (
        f"📊 YANGI SO'ROVNOMA\n"
        f"{'━' * 30}\n"
        f"👤 {name}\n"
        f"🏭 {dept}\n"
        f"🌐 {til}\n"
        f"{'━' * 30}\n\n"
    )
    for idx, (question, answer) in enumerate(zip(questions, answers)):
        num = NUM_EMOJI[idx] if idx < len(NUM_EMOJI) else f"{idx+1}."
        text += f"{num} {question}\n💬 {answer}\n\n"

    try:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    except Exception as e:
        logger.error(f"Guruhga yuborishda xatolik: {e}")

    context.user_data.clear()
    return ConversationHandler.END


async def restart_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer(cache_time=0)

    context.user_data.clear()
    context.user_data["del"] = []

    try:
        await q.message.delete()
    except Exception:
        pass

    elon_msg = await context.bot.send_message(chat_id=q.message.chat_id, text=ELON_TEXT)

    kb = [[
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="ru"),
    ]]
    msg = await context.bot.send_message(
        chat_id=q.message.chat_id,
        text="🌐 Tilni tanlang / Выберите язык:",
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return LANG


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    script = context.user_data.get("script", "lotin")

    if lang == "ru":
        text = "❌ Отменено. Нажмите /start."
    elif script == "kirill":
        text = "❌ Бекор қилинди. /start босинг."
    else:
        text = "❌ Bekor qilindi. /start bosing."

    await update.message.reply_text(text)
    context.user_data.clear()
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CallbackQueryHandler(restart_survey, pattern="^restart_survey$")],
        states={
            LANG: [CallbackQueryHandler(lang_chosen, pattern="^(uz|ru)$")],
            SCRIPT: [CallbackQueryHandler(script_chosen, pattern="^(lotin|kirill)$")],
            DEPARTMENT: [CallbackQueryHandler(dept_chosen, pattern="^dept_")],
            FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],
            SURVEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_answer),
                CommandHandler("start", start),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start), CallbackQueryHandler(restart_survey, pattern="^restart_survey$")],
        allow_reentry=True,
        conversation_timeout=3600,
    )
    app.add_handler(conv_handler)
    print("✅ Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
