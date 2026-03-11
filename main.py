from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TELEGRAM_TOKEN
from handlers import start, handle_message, handle_location, button_callback, subscribe, unsubscribe
from tasks import send_daily_weather
from datetime import time
import pytz


def main():
    if not TELEGRAM_TOKEN:
        print("❌ Błąd: Brak TELEGRAM_BOT_TOKEN w środowisku (lub .env).")
        return
        
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sub", subscribe))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsub", unsubscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Harmonogram: codziennie o 7:00
    # Używamy czasu lokalnego (Europe/Warsaw dla Polski)
    warsaw_tz = pytz.timezone("Europe/Warsaw")
    target_time = time(hour=7, minute=0, second=0, tzinfo=warsaw_tz)
    
    if application.job_queue:
        application.job_queue.run_daily(send_daily_weather, time=target_time)
        print("📅 Harmonogram ustawiony na 07:00 rano.")
    else:
        print("⚠️ Warning: JobQueue is not available. Daily forecasts won't work.")

    
    print("Bot uruchomiony... (Naciśnij Ctrl+C, aby zatrzymać)")
    application.run_polling()

if __name__ == "__main__":
    main()
