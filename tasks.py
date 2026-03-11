import asyncio
from datetime import time
from telegram.ext import ContextTypes
from weather_api import fetch_weather_data
from messages import format_weather_message
from subscriptions import load_subscriptions

async def send_daily_weather(context: ContextTypes.DEFAULT_TYPE):
    subscriptions = load_subscriptions()
    if not subscriptions:
        return

    print(f"⏰ Uruchamiam wysyłkę codziennej prognozy dla {len(subscriptions)} użytkowników...")
    
    loop = asyncio.get_event_loop()
    
    for chat_id, city in subscriptions.items():
        try:
            # Pobieramy dane pogodowe
            data = await loop.run_in_executor(None, fetch_weather_data, city, 2)
            
            # Formatujemy wiadomość
            msg, reply_markup = format_weather_message(data, city, is_tomorrow=False)
            
            # Wysyłamy wiadomość
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🌅 *Dzień dobry! Oto Twoja poranna prognoza dla {city}:*\n\n{msg}",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            print(f"✅ Wysłano prognozę do {chat_id} ({city})")
            
            # Mały odstęp, aby nie przekroczyć limitów Telegrama
            await asyncio.sleep(0.05)
            
        except Exception as e:
            print(f"❌ Błąd podczas wysyłania do {chat_id}: {e}")
