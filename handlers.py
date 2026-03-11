import io
import time
import asyncio
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from config import CACHE_EXPIRATION_SECONDS, WEATHER_STICKERS
from cache import CHART_CACHE, invalidate_caches
from weather_api import fetch_weather_data
from charts import generate_feelslike_chart
from messages import format_weather_message, get_help_message, get_sticker_message, get_unknown_command_message
from subscriptions import save_subscription, remove_subscription, load_subscriptions


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📍 Wyślij moją lokalizację", request_location=True)],
        [KeyboardButton("Wrocław"), KeyboardButton("Warszawa")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Hej! Jestem Twoim zaawansowanym botem pogodowym.\n\n"
        "Możesz u mnie sprawdzić pogodę na kilka sposobów:\n"
        "1️⃣ Wpisz z klawiatury nazwę *dowolnego miasta* (np. Paryż, Radom)\n"
        "2️⃣ Użyj przycisków na dole ekranu\n"
        "3️⃣ Prześlij swoją lokalizację z użyciem GPS\n\n"
        "🔔 *Subskrypcja:*\n"
        "Możesz wpisać `/sub Miasto` lub po prostu sprawdzić pogodę i kliknąć przycisk *Subskrybuj* pod wynikami!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
        
    # Szybkie sprawdzenie czy to powitanie
    greetings = ["cześć", "czesc", "hej", "siema", "hello", "hi", "dzień dobry", "dzien dobry"]
    if text.lower().strip() in greetings:
        await update.message.reply_text(
            f"👋 Hej! Miło Cię widzieć. Chcesz sprawdzić pogodę? \n\n"
            "Wpisz nazwę miasta (np. 'Berlin') lub wyślij mi swoją lokalizację! 📍",
            parse_mode="Markdown"
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
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
    
    if action.startswith("chart"):
        day_index = 1 if action == "charttomorrow" else 0
        cache_key = f"{city}_tomorrow" if day_index == 1 else city
        current_time = time.time()
        
        if cache_key in CHART_CACHE:
            cached = CHART_CACHE[cache_key]
            if current_time - cached["timestamp"] < CACHE_EXPIRATION_SECONDS:
                await query.message.reply_photo(
                    photo=io.BytesIO(cached["buffer"]),
                    caption=f"📈 *Wykres pogodowy (24h) dla {city}{' (Jutro)' if day_index == 1 else ''}*",
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
                caption=f"📈 *Wykres pogodowy (24h) dla {city}{' (Jutro)' if day_index == 1 else ''}*",
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_text("❌ Nie udało się wygenerować wykresu.")
        return

    if action == "sub":
        save_subscription(query.message.chat_id, city)
        await query.message.reply_text(f"✅ Subskrypcja aktywna! Prognoza dla *{city}* będzie wysyłana codziennie o 7:00.", parse_mode="Markdown")
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

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Podaj nazwę miasta, np.: `/sub Wrocław`", parse_mode="Markdown")
        return
    
    city = " ".join(context.args)
    save_subscription(update.effective_chat.id, city)
    await update.message.reply_text(f"✅ Będę Ci wysyłać prognozę dla *{city}* codziennie o 7:00!", parse_mode="Markdown")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if remove_subscription(update.effective_chat.id):
        await update.message.reply_text("🔕 Subskrypcja została anulowana.")
    else:
        await update.message.reply_text("ℹ️ Nie masz aktywnej subskrypcji.")

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Wyślij tekstową odpowiedź
    await update.message.reply_text(get_sticker_message(), parse_mode="Markdown")
    
    # Wyślij losową naklejkę pogodową
    if WEATHER_STICKERS:
        try:
            await context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=random.choice(WEATHER_STICKERS)
            )
        except Exception as e:
            print(f"⚠️ Błąd podczas wysyłania naklejki: {e}")
            # Ups, ID naklejki może być niepoprawne lub wygasło
            pass

async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(
        "🤔 Wygląda na to, że wysłałeś coś, czego jeszcze nie potrafię przetworzyć.\n\n"
        "Skupiam się na sprawdzaniu pogody! Wpisz nazwę miasta, aby zacząć. 🌤️",
        parse_mode="Markdown"
    )

async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(get_unknown_command_message(), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(get_help_message(), parse_mode="Markdown")

