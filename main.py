from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.core.config import TELEGRAM_TOKEN
from bot.handlers import (
    start, handle_message, handle_location, button_callback, 
    subscribe, unsubscribe, help_command, handle_sticker, 
    handle_unknown_command, handle_unsupported
)
from bot.tasks.daily import send_daily_weather
from datetime import time
import pytz


def main():
    if not TELEGRAM_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN is missing from environment (or .env).")
        return
        
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
    except Exception as e:
        print(f"❌ Critical error during bot initialization: {e}")
        print("💡 Suggestion: Try installing: 'pip install python-telegram-bot[job-queue] APScheduler' --upgrade")
        return

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sub", subscribe))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsub", unsubscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    
    # Unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))
    
    # Text (cities) - handle after commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Stickers
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    
    # Other formats
    application.add_handler(MessageHandler(filters.ALL & ~filters.TEXT & ~filters.LOCATION & ~filters.Sticker.ALL & ~filters.COMMAND, handle_unsupported))
    
    # Location
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Schedule: every day at 7:00 AM
    # Using local time (Europe/Warsaw)
    warsaw_tz = pytz.timezone("Europe/Warsaw")
    target_time = time(hour=7, minute=0, second=0, tzinfo=warsaw_tz)
    
    if application.job_queue:
        application.job_queue.run_daily(send_daily_weather, time=target_time)
        print("📅 Schedule set to 07:00 AM daily (Europe/Warsaw).")
    else:
        print("⚠️ Warning: JobQueue is not available. Daily forecasts won't work.")

    print("Bot started... (Press Ctrl+C to stop)")
    application.run_polling()

if __name__ == "__main__":
    main()
