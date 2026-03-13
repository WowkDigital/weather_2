import io
import time
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from bot.core.config import CACHE_EXPIRATION_SECONDS
from bot.core.cache import CHART_CACHE, invalidate_caches
from bot.services.weather import fetch_weather_data
from bot.services.charts import generate_feelslike_chart
from bot.core.messages import format_weather_message
from bot.core.subscriptions import save_subscription

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
        
    # Quick check for greetings
    greetings = ["hi", "hello", "hey", "good morning", "morning"]
    if text.lower().strip() in greetings:
        await update.message.reply_text(
            f"👋 Hey! Nice to see you. Want to check the weather? \n\n"
            "Type a city name (e.g., 'Berlin') or send me your location! 📍",
            parse_mode="Markdown"
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    loading_msg = await update.message.reply_text(f"⏳ Checking weather for: {text}...")
    
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, fetch_weather_data, text, 2)
    
    msg, reply_markup = format_weather_message(data, text, is_tomorrow=False)
    
    try:
        await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        await loading_msg.edit_text(msg, parse_mode="Markdown")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    query = f"{lat},{lon}"
    
    loading_msg = await update.message.reply_text("⏳ Checking clouds in your area...")
    
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, fetch_weather_data, query, 2)
    
    city_name = data.get("location", {}).get("name", "your location") if "error" not in data else query
    msg, reply_markup = format_weather_message(data, city_name, is_tomorrow=False)
    
    try:
        await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        await loading_msg.edit_text(msg, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data_str = query.data
    action, city = data_str.split("_", 1)
    
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, fetch_weather_data, city, 2)
    
    if action.startswith("chart"):
        day_index = 1 if action == "charttomorrow" else 0
        cache_key = f"{city}_tomorrow" if day_index == 1 else city
        current_time = time.time()
        
        if cache_key in CHART_CACHE:
            cached = CHART_CACHE[cache_key]
            if current_time - cached["timestamp"] < CACHE_EXPIRATION_SECONDS:
                await query.message.reply_photo(
                    photo=io.BytesIO(cached["buffer"]),
                    caption=f"📈 *Weather Chart (24h) for {city}{' (Tomorrow)' if day_index == 1 else ''}*",
                    parse_mode="Markdown"
                )
                return

        chart_buf = await loop.run_in_executor(None, generate_feelslike_chart, data, city, day_index)
        if chart_buf:
            chart_bytes = chart_buf.getvalue()
            CHART_CACHE[cache_key] = {"buffer": chart_bytes, "timestamp": time.time()}
            
            chart_buf.seek(0)
            await query.message.reply_photo(
                photo=chart_buf,
                caption=f"📈 *Weather Chart (24h) for {city}{' (Tomorrow)' if day_index == 1 else ''}*",
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_text("❌ Failed to generate chart.")
        return

    if action == "sub":
        save_subscription(query.message.chat_id, city)
        await query.message.reply_text(f"✅ Subscription active! Forecast for *{city}* will be sent daily at 7:00 AM.", parse_mode="Markdown")
        return

    is_tomorrow = (action in ["tomorrow", "moretomorrow", "charttomorrow"])
    full_details = (action in ["more", "moretomorrow"])
    
    if action == "refresh":
        invalidate_caches(city)
        data = await loop.run_in_executor(None, fetch_weather_data, city, 2)

    msg, reply_markup = format_weather_message(data, city, is_tomorrow=is_tomorrow, full_details=full_details)
    
    try:
        await query.edit_message_text(text=msg, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        pass
