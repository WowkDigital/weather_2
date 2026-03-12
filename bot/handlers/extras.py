import random
from telegram import Update
from telegram.ext import ContextTypes
from bot.core.config import WEATHER_STICKERS
from bot.core.messages import get_sticker_message, get_unknown_command_message

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(get_sticker_message(), parse_mode="Markdown")
    
    if WEATHER_STICKERS:
        try:
            await context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=random.choice(WEATHER_STICKERS)
            )
        except Exception as e:
            print(f"⚠️ Error sending sticker: {e}")
            pass

async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(
        "🤔 It looks like you sent something I don't know how to process yet.\n\n"
        "I'm focusing on checking the weather! Type a city name to start. 🌤️",
        parse_mode="Markdown"
    )

async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(get_unknown_command_message(), parse_mode="Markdown")
