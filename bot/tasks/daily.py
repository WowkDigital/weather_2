import asyncio
from telegram.ext import ContextTypes
from bot.services.weather import fetch_weather_data
from bot.core.messages import format_weather_message
from bot.core.subscriptions import load_subscriptions

async def send_daily_weather(context: ContextTypes.DEFAULT_TYPE):
    subscriptions = load_subscriptions()
    if not subscriptions:
        return

    print(f"⏰ Starting daily forecast delivery for {len(subscriptions)} users...")
    
    loop = asyncio.get_event_loop()
    
    for chat_id, city in subscriptions.items():
        try:
            # Fetch weather data
            data = await loop.run_in_executor(None, fetch_weather_data, city, 2)
            
            # Format message
            msg, reply_markup = format_weather_message(data, city, is_tomorrow=False)
            
            # Send message
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🌅 *Good morning! Here is your morning forecast for {city}:*\n\n{msg}",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            print(f"✅ Forecast sent to {chat_id} ({city})")
            
            # Small delay to respect Telegram API limits
            await asyncio.sleep(0.05)
            
        except Exception as e:
            print(f"❌ Error sending to {chat_id}: {e}")
