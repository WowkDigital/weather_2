from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TELEGRAM_TOKEN
from handlers import (
    start, handle_message, handle_location, button_callback, 
    subscribe, unsubscribe, help_command, handle_sticker, 
    handle_unknown_command, handle_unsupported
)
from tasks import send_daily_weather
from datetime import time
import pytz


def main():
    if not TELEGRAM_TOKEN:
        print("❌ Błąd: Brak TELEGRAM_BOT_TOKEN w środowisku (lub .env).")
        return
        
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
    except Exception as e:
        print(f"❌ Krytyczny błąd podczas inicjalizacji bota: {e}")
        print("💡 Sugestia: Spróbuj zainstalować: 'pip install python-telegram-bot[job-queue] APScheduler' --upgrade")
        return

    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sub", subscribe))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsub", unsubscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    
    # Obsługa nieznanych komend
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))
    
    # Tekst (miasta) - obsługa po komendach
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Naklejki
    application.add_handler(MessageHandler(filters.STICKER, handle_sticker))
    
    # Inne (np. zdjęcia, pliki) - podajmy przyjazny komunikat o nieobsługiwanym formacie
    application.add_handler(MessageHandler(filters.ALL & ~filters.TEXT & ~filters.LOCATION & ~filters.STICKER & ~filters.COMMAND, handle_unsupported))
    
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
