from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from bot.core.messages import get_help_message
from bot.core.subscriptions import save_subscription, remove_subscription
from bot.core.utils import normalize_city_name

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📍 Send my location", request_location=True)],
        [KeyboardButton("Wrocław"), KeyboardButton("Warszawa")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Hey! I'm your advanced weather bot.\n\n"
        "You can check the weather in several ways:\n"
        "1️⃣ Type the name of *any city* (e.g., Paris, Tokyo)\n"
        "2️⃣ Use the buttons at the bottom\n"
        "3️⃣ Send your location using GPS\n\n"
        "🔔 *Subscription:*\n"
        "You can type `/sub City` or just check the weather and click the *Subscribe* button under the results!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(get_help_message(), parse_mode="Markdown")
