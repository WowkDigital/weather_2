from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TELEGRAM_TOKEN
from handlers import start, handle_message, handle_location, button_callback

def main():
    if not TELEGRAM_TOKEN:
        print("❌ Błąd: Brak TELEGRAM_BOT_TOKEN w środowisku (lub .env).")
        return
        
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot uruchomiony... (Naciśnij Ctrl+C, aby zatrzymać)")
    application.run_polling()

if __name__ == "__main__":
    main()
