import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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

def get_weather(city: str) -> str:
    if not WEATHER_API_KEY:
        return "⚠️ Weather API key is not configured."
    
    # Send a request to the API
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=no&alerts=no"
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"❌ Failed to get weather data for {city}. Please try again later."
    
    data = response.json()
    
    # Extract Real-time data
    current = data.get("current", {})
    temp_c = current.get("temp_c", "N/A")
    humidity = current.get("humidity", "N/A")
    wind_kph = current.get("wind_kph", "N/A")
    condition_text = current.get("condition", {}).get("text", "N/A")
    precip_mm = current.get("precip_mm", 0)
    
    is_raining = "Yes 🌧️" if precip_mm > 0 or "rain" in condition_text.lower() else "No 🚫"
    
    # Extract Forecast data for today
    try:
        forecast_today = data.get("forecast", {}).get("forecastday", [{}])[0]
        day = forecast_today.get("day", {})
        maxtemp_c = day.get("maxtemp_c", "N/A")
        chance_of_rain = day.get("daily_chance_of_rain", "N/A")
        
        astro = forecast_today.get("astro", {})
        sunset_str = astro.get("sunset", "N/A")
        moon_phase = astro.get("moon_phase", "N/A")
    except (IndexError, AttributeError):
        maxtemp_c = "N/A"
        chance_of_rain = "N/A"
        sunset_str = "N/A"
        moon_phase = "N/A"
    
    # Get local time and parse remaining sun and 24h format
    localtime_str = data.get("location", {}).get("localtime", "")
    
    sunset_24h = "N/A"
    remaining_sun = "N/A"
    
    try:
        if sunset_str != "N/A" and localtime_str:
            # localtime format from weatherapi: "2023-10-25 15:30"
            local_dt = datetime.strptime(localtime_str, "%Y-%m-%d %H:%M")
            # sunset format: "05:45 PM"
            sunset_time = datetime.strptime(sunset_str, "%I:%M %p")
            
            # Combine the date of local time with the time of sunset
            sunset_full_dt = local_dt.replace(hour=sunset_time.hour, minute=sunset_time.minute, second=0, microsecond=0)
            
            # Format to 24-hour style
            sunset_24h = sunset_full_dt.strftime("%H:%M")
            
            # Calculate difference
            if local_dt >= sunset_full_dt:
                remaining_sun = "0h 0m - Sun has set 🌃"
            else:
                diff = sunset_full_dt - local_dt
                hours, remainder = divmod(diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                remaining_sun = f"{hours}h {minutes}m ☀️"
    except Exception as e:
        # Fallback if there is a parsing error
        pass
        
    moon_emoji = MOON_EMOJIS.get(moon_phase, "🌙")
    
    # Constructing the message
    msg = (f"🌍 *Weather in {city}*\n\n"
           f"🌡️ *Temperature:* {temp_c}°C (Max today: {maxtemp_c}°C)\n"
           f"☁️ *Sky condition:* {condition_text}\n"
           f"💧 *Humidity:* {humidity}%\n"
           f"💨 *Wind:* {wind_kph} km/h\n"
           f"🌧️ *Raining now?* {is_raining}\n"
           f"☔ *Chance of rain today:* {chance_of_rain}%\n\n"
           f"🌇 *Sunset time:* {sunset_24h}\n"
           f"⏳ *Remaining sunlight:* {remaining_sun}\n\n"
           f"✨ *Moon phase:* {moon_phase} {moon_emoji}")
    
    return msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Keyboard setup with two cities
    keyboard = [
        ["Wrocław", "Warszawa"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Hello! I am your simple weather bot.\nChoose a city to get the current weather report:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ["Wrocław", "Warszawa"]:
        # Respond with weather data
        weather_info = get_weather(text)
        await update.message.reply_text(weather_info, parse_mode="Markdown")
    else:
        await update.message.reply_text("Please select a city from the keyboard buttons below.")

def main():
    if not TELEGRAM_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN is missing in the environment or .env file.")
        return
        
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting... (Press Ctrl+C to stop)")
    application.run_polling()

if __name__ == "__main__":
    main()
