import io
import time
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from config import CACHE_EXPIRATION_SECONDS
from cache import CHART_CACHE, invalidate_caches
from weather_api import fetch_weather_data
from charts import generate_feelslike_chart
from messages import format_weather_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📍 Wyślij moją lokalizację", request_location=True)],
        [KeyboardButton("Wrocław"), KeyboardButton("Warszawa")],
        [KeyboardButton("Kraków"), KeyboardButton("Gdańsk")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Hej! Jestem Twoim zaawansowanym botem pogodowym.\n\n"
        "Możesz u mnie sprawdzić pogodę na kilka sposobów:\n"
        "1️⃣ Wpisz z klawiatury nazwę *dowolnego miasta* (np. Paryż, Radom)\n"
        "2️⃣ Użyj przycisków na dole ekranu\n"
        "3️⃣ Prześlij swoją lokalizację z użyciem GPS",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
        
    loading_msg = await update.message.reply_text(f"⏳ Sprawdzam pogodę dla: {text}...")
    
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
    
    loading_msg = await update.message.reply_text("⏳ Sprawdzam chmury w Twojej okolicy...")
    
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, fetch_weather_data, query, 2)
    
    city_name = data.get("location", {}).get("name", "Twojej lokacji") if "error" not in data else query
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
    
    if action == "chart":
        current_time = time.time()
        if city in CHART_CACHE:
            cached = CHART_CACHE[city]
            if current_time - cached["timestamp"] < CACHE_EXPIRATION_SECONDS:
                await query.message.reply_photo(
                    photo=io.BytesIO(cached["buffer"]),
                    caption=f"📈 *[Kesz] Wykres temperatury odczuwalnej (24h) dla {city}*",
                    parse_mode="Markdown"
                )
                return

        chart_buf = await loop.run_in_executor(None, generate_feelslike_chart, data, city)
        if chart_buf:
            chart_bytes = chart_buf.getvalue()
            CHART_CACHE[city] = {"buffer": chart_bytes, "timestamp": time.time()}
            
            chart_buf.seek(0)
            await query.message.reply_photo(
                photo=chart_buf,
                caption=f"📈 *Wykres temperatury odczuwalnej (24h) dla {city}*",
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_text("❌ Nie udało się wygenerować wykresu.")
        return

    is_tomorrow = (action == "tomorrow")
    
    if action == "refresh":
        invalidate_caches(city)
        data = await loop.run_in_executor(None, fetch_weather_data, city, 2)

    msg, reply_markup = format_weather_message(data, city, is_tomorrow=is_tomorrow)
    
    try:
        await query.edit_message_text(text=msg, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        pass
