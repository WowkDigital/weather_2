import os
import requests
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Load env variables safely
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

MOON_EMOJIS = {
    "New Moon": "🌑",
    "Waxing Crescent": "🌒",
    "First Quarter": "🌓",
    "Waxing Gibbous": "🌔",
    "Full Moon": "🌕",
    "Waning Gibbous": "🌖",
    "Last Quarter": "🌗",
    "Waning Crescent": "🌘"
}

def fetch_weather_data(city: str, days: int = 1) -> dict:
    if not WEATHER_API_KEY:
        return {"error": "⚠️ Brak klucza API. Skonfiguruj zmienną WEATHER_API_KEY."}
    
    # Mapping for cities that might have Polish characters
    city_map = {
        "Wrocław": "Wroclaw",
        "Kraków": "Krakow",
        "Gdańsk": "Gdansk",
        "Poznań": "Poznan",
        "Łódź": "Lodz"
    }
    query_city = city_map.get(city, city)
    
    # Send a request to the API
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": query_city,
        "days": days,
        "aqi": "yes",
        "alerts": "yes",
        "lang": "pl"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return {"error": f"❌ Nie udało się pobrać danych dla {city}. Upewnij się, że nazwa miasta jest poprawna."}
        return response.json()
    except Exception:
        return {"error": f"❌ Błąd sieci przy pobieraniu danych dla {city}."}

def format_weather_message(data: dict, city: str, is_tomorrow: bool = False) -> tuple:
    if "error" in data:
        return data["error"], None
        
    location = data.get("location", {})
    actual_city = location.get("name", city)
    country = location.get("country", "")
    
    forecast_days = data.get("forecast", {}).get("forecastday", [])
    current = data.get("current", {})
    
    if is_tomorrow and len(forecast_days) > 1:
        target_day_data = forecast_days[1]
        date_str = target_day_data.get("date", "")
        day = target_day_data.get("day", {})
        
        temp_c = day.get("avgtemp_c", "N/A")
        feelslike_c = "N/A" # Daily averages don't have feelslike
        humidity = day.get("avghumidity", "N/A")
        wind_kph = day.get("maxwind_kph", "N/A")
        condition_text = day.get("condition", {}).get("text", "N/A")
        precip_mm = day.get("totalprecip_mm", 0)
        uv = day.get("uv", "N/A")
        
        chance_of_rain = day.get("daily_chance_of_rain", "N/A")
        try:
            is_raining = "Tak 🌧️" if int(chance_of_rain) > 50 else "Nie 🚫"
        except (ValueError, TypeError):
            is_raining = "Nieznane"
            
        maxtemp_c = day.get("maxtemp_c", "N/A")
        mintemp_c = day.get("mintemp_c", "N/A")
        
        astro = target_day_data.get("astro", {})
        sunset_str = astro.get("sunset", "N/A")
        moon_phase = astro.get("moon_phase", "N/A")
        
        pressure_mb = "N/A"
        gust_kph = "N/A"
        aqi_index = "N/A"
        
        header = f"📅 *Pogoda na jutro ({date_str}) w {actual_city}, {country}*"
    else:
        target_day_data = forecast_days[0] if forecast_days else {}
        day = target_day_data.get("day", {})
        
        temp_c = current.get("temp_c", "N/A")
        feelslike_c = current.get("feelslike_c", "N/A")
        humidity = current.get("humidity", "N/A")
        wind_kph = current.get("wind_kph", "N/A")
        gust_kph = current.get("gust_kph", "N/A")
        condition_text = current.get("condition", {}).get("text", "N/A")
        precip_mm = current.get("precip_mm", 0)
        pressure_mb = current.get("pressure_mb", "N/A")
        uv = current.get("uv", "N/A")
        
        air_quality = current.get("air_quality", {})
        aqi_index = air_quality.get("gb-defra-index", "N/A")
        if aqi_index != "N/A":
            try:
                aqi_int = int(aqi_index)
                if aqi_int <= 3: aqi_index = f"{aqi_int} (Dobra 🟢)"
                elif aqi_int <= 6: aqi_index = f"{aqi_int} (Umiarkowana 🟡)"
                else: aqi_index = f"{aqi_int} (Zła 🔴)"
            except ValueError:
                pass
                
        chance_of_rain = day.get("daily_chance_of_rain", "N/A")
        is_raining = "Tak 🌧️" if precip_mm > 0 else "Nie 🚫"
        
        maxtemp_c = day.get("maxtemp_c", "N/A")
        mintemp_c = day.get("mintemp_c", "N/A")
        
        astro = target_day_data.get("astro", {})
        sunset_str = astro.get("sunset", "N/A")
        moon_phase = astro.get("moon_phase", "N/A")
        
        header = f"🌍 *Aktualna pogoda w {actual_city}, {country}*"

    # Format sunset specifically to 24h
    sunset_24h = "N/A"
    try:
        if sunset_str != "N/A":
            sunset_time = datetime.strptime(sunset_str, "%I:%M %p")
            sunset_24h = sunset_time.strftime("%H:%M")
    except Exception:
        pass

    moon_emoji = MOON_EMOJIS.get(moon_phase, "🌙")
    
    # Check for alerts
    alerts_data = data.get("alerts", {}).get("alert", [])
    alerts_text = ""
    # Usually alerts make more sense for today's forecast or general alerts
    if alerts_data and not is_tomorrow:
        alerts_text = "\n\n⚠️ *Ostrzeżenia pogodowe:*\n"
        for alert in alerts_data[:2]:
            event = alert.get("event", "Ostrzeżenie")
            alerts_text += f"❗ {event}\n"

    msg = (f"{header}\n\n"
           f"🌡️ *Temperatura:* {temp_c}°C {f'(Odczuwalna: {feelslike_c}°C)' if feelslike_c != 'N/A' else ''}\n"
           f"📉 *Min/Max:* {mintemp_c}°C / {maxtemp_c}°C\n"
           f"☁️ *Warunki:* {condition_text}\n"
           f"💧 *Wilgotność:* {humidity}%\n"
           f"{f'🧭 *Ciśnienie:* {pressure_mb} hPa' if pressure_mb != 'N/A' else ''}\n"
           f"💨 *Wiatr:* {wind_kph} km/h {f'(W porywach: {gust_kph} km/h)' if gust_kph != 'N/A' else ''}\n"
           f"🌧️ *Opady:* {is_raining} (Szansa: {chance_of_rain}%)\n"
           f"{f'☀️ *Indeks UV:* {uv}' if uv != 'N/A' else ''}\n"
           f"{f'😷 *Jakość powietrza (AQI):* {aqi_index}' if aqi_index != 'N/A' else ''}\n\n"
           f"🌇 *Zachód słońca:* {sunset_24h}\n"
           f"✨ *Faza księżyca:* {moon_phase} {moon_emoji}{alerts_text}")
           
    # Clean up empty lines that might occur if some fields are N/A and not shown
    msg = "\n".join([line for line in msg.split("\n") if line.strip() != ""])
    msg = msg.replace("\n\n\n", "\n\n")

    # Create inline keyboard for toggles
    keyboard = []
    if is_tomorrow:
        keyboard.append([InlineKeyboardButton("🔙 Pogoda na dzisiaj", callback_data=f"today_{city}")])
    else:
        keyboard.append([InlineKeyboardButton("📅 Pogoda na jutro", callback_data=f"tomorrow_{city}")])
        
    keyboard.append([InlineKeyboardButton("🔄 Odśwież", callback_data=f"refresh_{city}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    return msg, reply_markup

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
    
    is_tomorrow = (action == "tomorrow")
    msg, reply_markup = format_weather_message(data, city, is_tomorrow=is_tomorrow)
    
    try:
        await query.edit_message_text(text=msg, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        pass

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
