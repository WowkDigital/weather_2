import os
import requests
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import matplotlib.pyplot as plt
import io

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

# Caching Configuration
CACHE_EXPIRATION_SECONDS = 900  # 15 minutes
WEATHER_CACHE = {}  # Format: {city: {"data": data, "timestamp": timestamp}}
CHART_CACHE = {}    # Format: {city: {"buffer": bytes, "timestamp": timestamp}}

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
    
    # Check Cache
    current_time = time.time()
    if city in WEATHER_CACHE:
        cached = WEATHER_CACHE[city]
        if current_time - cached["timestamp"] < CACHE_EXPIRATION_SECONDS:
            return cached["data"]
    
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
        
        data = response.json()
        
        # Save to cache (only if valid)
        if "error" not in data:
            WEATHER_CACHE[city] = {"data": data, "timestamp": time.time()}
            # Invalidate chart cache for this city as data changed
            if city in CHART_CACHE:
                del CHART_CACHE[city]
                
        return data
    except Exception:
        return {"error": f"❌ Błąd sieci przy pobieraniu danych dla {city}."}

def get_temp_emoji(temp):
    try:
        t = float(temp)
        if t < 0: return "❄️"
        if t < 10: return "☁️"
        if t < 20: return "🌤️"
        if t < 30: return "☀️"
        return "🔥"
    except: return "🌡️"

def get_feelslike_emoji(t):
    try:
        t = float(t)
        if t < 5: return "🥶"
        if t < 25: return "🌡️"
        return "🥵"
    except: return "🌡️"

def get_visual_scale(value, max_val=100, emoji="▫️", empty_char="—", alt_zero=None):
    try:
        val = float(value)
        steps = int(round((val / max_val) * 4))
        steps = max(0, min(4, steps))
        
        if steps == 0 and alt_zero:
            return f"{alt_zero} — — —"
        
        scale = [emoji] * steps + [empty_char] * (4 - steps)
        return " ".join(scale)
    except: return "— — — —"

def get_wind_emoji(speed):
    try:
        s = float(speed)
        if s < 10: return "🍃"
        if s < 30: return "🌬️"
        if s < 60: return "💨"
        return "🌪️"
    except: return "💨"

def get_uv_emoji(uv):
    try:
        u = float(uv)
        if u <= 2: return "✅"
        if u <= 5: return "🟡"
        if u <= 7: return "🟠"
        if u <= 10: return "🔴"
        return "🟣"
    except: return "☀️"

def generate_feelslike_chart(data: dict, city: str):
    forecast_days = data.get("forecast", {}).get("forecastday", [])
    if not forecast_days:
        return None
        
    all_hours = []
    for day in forecast_days:
        all_hours.extend(day.get("hour", []))
    
    local_time_str = data.get("location", {}).get("localtime", "")
    try:
        current_time = datetime.strptime(local_time_str, "%Y-%m-%d %H:%M")
    except:
        current_time = datetime.now()
        
    relevant_hours = [h for h in all_hours if datetime.strptime(h["time"], "%Y-%m-%d %H:%M") >= current_time][:24]
    
    if not relevant_hours:
        relevant_hours = all_hours[:24]
        
    times = []
    temps = []
    for h in relevant_hours:
        time_part = h["time"].split(" ")[1]
        times.append(time_part)
        temps.append(h["feelslike_c"])
        
    plt.figure(figsize=(10, 5))
    plt.plot(times, temps, marker='o', linestyle='-', color='#00d2ff', linewidth=3, markersize=8)
    
    # Add annotations for each point
    for i, (time, temp) in enumerate(zip(times, temps)):
        if i % 2 == 0: # Show every second label to avoid crowding
            plt.annotate(f"{temp}°", (time, temp), textcoords="offset points", xytext=(0,10), ha='center', color='white', fontsize=10)

    plt.title(f"Temperatura odczuwalna (24h) - {city}", fontsize=16, color='white', fontweight='bold', pad=20)
    plt.xlabel("Godzina", fontsize=12, color='white', labelpad=10)
    plt.ylabel("Temperatura (°C)", fontsize=12, color='white', labelpad=10)
    
    # Styling axes
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    plt.grid(True, linestyle='--', alpha=0.2, color='white')
    
    # Removing top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['left'].set_color('white')
    
    # Background color
    plt.gcf().set_facecolor('#1a1a1a')
    plt.gca().set_facecolor('#1a1a1a')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, facecolor='#1a1a1a')
    buf.seek(0)
    plt.close()
    return buf

def format_weather_message(data: dict, city: str, is_tomorrow: bool = False) -> tuple:
    if "error" in data:
        return data["error"], None
        
    location = data.get("location", {})
    actual_city = location.get("name", city)
    country = location.get("country", "")
    local_time = location.get("localtime", "N/A")
    
    forecast_days = data.get("forecast", {}).get("forecastday", [])
    current = data.get("current", {})
    
    if is_tomorrow and len(forecast_days) > 1:
        target_day_data = forecast_days[1]
        date_str = target_day_data.get("date", "")
        day = target_day_data.get("day", {})
        
        temp_c = day.get("avgtemp_c", "N/A")
        maxtemp_c = day.get("maxtemp_c", "N/A")
        mintemp_c = day.get("mintemp_c", "N/A")
        feelslike_c = "N/A"
        humidity = day.get("avghumidity", "N/A")
        wind_kph = day.get("maxwind_kph", "N/A")
        condition_text = day.get("condition", {}).get("text", "N/A")
        uv = day.get("uv", "N/A")
        chance_of_rain = day.get("daily_chance_of_rain", 0)
        clouds = day.get("cloud", 50) # Forecast total cloud not directly in simple day model
        pressure_mb = "N/A"
        gust_kph = "N/A"
        aqi_index = "N/A"
        
        header = f"📅 *POGODA NA JUTRO*\n📍 {actual_city}, {country}\n🗓️ Data: {date_str}"
    else:
        target_day_data = forecast_days[0] if forecast_days else {}
        day = target_day_data.get("day", {})
        
        temp_c = current.get("temp_c", "N/A")
        feelslike_c = current.get("feelslike_c", "N/A")
        humidity = current.get("humidity", "N/A")
        wind_kph = current.get("wind_kph", "N/A")
        gust_kph = current.get("gust_kph", "N/A")
        condition_text = current.get("condition", {}).get("text", "N/A")
        pressure_mb = current.get("pressure_mb", "N/A")
        uv = current.get("uv", "N/A")
        clouds = current.get("cloud", 0)
        
        air_quality = current.get("air_quality", {})
        aqi_index = air_quality.get("gb-defra-index", "N/A")
        
        chance_of_rain = day.get("daily_chance_of_rain", 0)
        maxtemp_c = day.get("maxtemp_c", "N/A")
        mintemp_c = day.get("mintemp_c", "N/A")
        
        header = f"🌍 *AKTUALNA POGODA*\n📍 {actual_city}, {country}\n🕒 Czas: {local_time}"

    # Visual Scales
    cloud_scale = get_visual_scale(clouds, 100, "☁️", "—", "✨")
    humidity_scale = get_visual_scale(humidity, 100, "💧")
    wind_scale = get_visual_scale(wind_kph, 80, "🌬️", "—", "🍃") # 80 is high wind
    rain_scale = get_visual_scale(chance_of_rain, 100, "🌧️")
    
    # Emojis
    temp_icon = get_temp_emoji(temp_c)
    feels_icon = get_feelslike_emoji(feelslike_c) if feelslike_c != "N/A" else "🌡️"
    uv_icon = get_uv_emoji(uv)
    
    # AQI
    aqi_desc = ""
    if aqi_index != "N/A":
        try:
            val = int(aqi_index)
            if val <= 3: aqi_desc = "Dobra 🟢"
            elif val <= 6: aqi_desc = "Średnia 🟡"
            else: aqi_desc = "Zła 🔴"
        except: aqi_desc = str(aqi_index)

    # Astronomy
    astro = target_day_data.get("astro", {})
    sunrise_24h = "N/A"
    sunset_24h = "N/A"
    try:
        if astro.get("sunrise") and astro.get("sunset"):
            sunrise_24h = datetime.strptime(astro["sunrise"], "%I:%M %p").strftime("%H:%M")
            sunset_24h = datetime.strptime(astro["sunset"], "%I:%M %p").strftime("%H:%M")
    except: pass

    # Alerts
    alerts_data = data.get("alerts", {}).get("alert", [])
    alerts_section = ""
    if alerts_data and not is_tomorrow:
        alerts_section = "\n⚠️ *AKTYWNE ALERTY:*\n" + "\n".join([f"{a.get('event')}" for a in alerts_data[:2]])

    msg = [
        header,
        "",
        "🌡️ *TEMPERATURA*",
        f"Aktualna: {temp_c}°C {temp_icon}",
        f"Odczuwalna: {feelslike_c}°C {feels_icon}" if feelslike_c != "N/A" else f"Zakres: {mintemp_c} - {maxtemp_c}°C 📉",
        "",
        "☁️ *NIEBO I WARUNKI*",
        f"Stan: {condition_text}",
        f"Chmury: [{cloud_scale}]",
        f"Opady: [{rain_scale}] {chance_of_rain}%",
        "",
        "💧 *SZCZEGÓŁY*",
        f"Wilgotność: [{humidity_scale}] {humidity}%",
        f"Indeks UV: {uv} {uv_icon}",
        f"Powietrze: {aqi_desc}" if aqi_desc else "",
        "",
        "💨 *WIATR I CIŚNIENIE*",
        f"Power: [{wind_scale}] {wind_kph} km/h",
        f"Porywy: {gust_kph} km/h" if gust_kph != "N/A" else "",
        f"Ciśnienie: {pressure_mb} hPa" if pressure_mb != "N/A" else "",
        "",
        "🌓 *ASTRONOMIA*",
        f"🌅 {sunrise_24h} | 🌇 {sunset_24h}",
        f"Księżyc: {astro.get('moon_phase', 'N/A')} {MOON_EMOJIS.get(astro.get('moon_phase'), '🌙')}",
        alerts_section
    ]

    # Łączymy linie, zachowując te puste dla lepszej czytelności
    final_msg = "\n".join([line for line in msg if line is not None]).strip()

    # Keyboard
    keyboard = []
    if is_tomorrow:
        keyboard.append([InlineKeyboardButton("🔙 Dzisiaj", callback_data=f"today_{city}")])
    else:
        keyboard.append([InlineKeyboardButton("📅 Jutro", callback_data=f"tomorrow_{city}")])
    
    keyboard.append([
        InlineKeyboardButton("� Wykres odczuwalnej", callback_data=f"chart_{city}"),
        InlineKeyboardButton("�🔄 Odśwież", callback_data=f"refresh_{city}")
    ])
    
    return final_msg, InlineKeyboardMarkup(keyboard)

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
        # Check Chart Cache
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
            # Save to cache
            chart_bytes = chart_buf.getvalue()
            CHART_CACHE[city] = {"buffer": chart_bytes, "timestamp": time.time()}
            
            # Reset buffer pointer for sending
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
    
    # Special case for refresh: force clearing cache for this city
    if action == "refresh":
        if city in WEATHER_CACHE:
            del WEATHER_CACHE[city]
        if city in CHART_CACHE:
            del CHART_CACHE[city]
        data = await loop.run_in_executor(None, fetch_weather_data, city, 2)

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
