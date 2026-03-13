from datetime import datetime
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from bot.core.config import MOON_EMOJIS
from bot.core.utils import get_temp_emoji, get_feelslike_emoji, get_visual_scale, get_wind_emoji, get_uv_emoji

def format_weather_message(data: dict, city: str, is_tomorrow: bool = False, full_details: bool = False) -> tuple:
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
        clouds = day.get("cloud", 50)
        pressure_mb = "N/A"
        gust_kph = "N/A"
        aqi_index = "N/A"
        
        header = f"📅 *TOMORROW'S WEATHER*\n📍 {actual_city}, {country}\n🗓️ Date: {date_str}"
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
        
        header = f"🌍 *CURRENT WEATHER*\n📍 {actual_city}, {country}\n🕒 Time: {local_time}"

    cloud_scale = get_visual_scale(clouds, 100, "☁️", "—", "✨")
    humidity_scale = get_visual_scale(humidity, 100, "💧")
    wind_scale = get_visual_scale(wind_kph, 80, "🌬️", "—", "🍃")
    rain_scale = get_visual_scale(chance_of_rain, 100, "🌧️")
    
    temp_icon = get_temp_emoji(temp_c)
    feels_icon = get_feelslike_emoji(feelslike_c) if feelslike_c != "N/A" else "🌡️"
    uv_icon = get_uv_emoji(uv)
    
    aqi_desc = ""
    if aqi_index != "N/A":
        try:
            val = int(aqi_index)
            if val <= 3: aqi_desc = "Good 🟢"
            elif val <= 6: aqi_desc = "Moderate 🟡"
            else: aqi_desc = "Poor 🔴"
        except: aqi_desc = str(aqi_index)
 
    astro = target_day_data.get("astro", {})
    sunrise_24h = "N/A"
    sunset_24h = "N/A"
    try:
        if astro.get("sunrise") and astro.get("sunset"):
            sunrise_24h = datetime.strptime(astro["sunrise"], "%I:%M %p").strftime("%H:%M")
            sunset_24h = datetime.strptime(astro["sunset"], "%I:%M %p").strftime("%H:%M")
    except: pass

    alerts_data = data.get("alerts", {}).get("alert", [])
    alerts_section = ""
    if alerts_data and not is_tomorrow:
        alerts_section = "\n⚠️ *ACTIVE ALERTS:*\n" + "\n".join([f"{a.get('event')}" for a in alerts_data[:2]])

    msg = [
        header,
        "",
        "🌡️ *TEMPERATURE*",
        f"Current: {temp_c}°C {temp_icon}",
        f"Feels like: {feelslike_c}°C {feels_icon}" if feelslike_c != "N/A" else f"Range: {mintemp_c} - {maxtemp_c}°C 📉",
        "",
        "☁️ *SKY & CONDITIONS*",
        f"Condition: {condition_text}",
        f"Clouds: [{cloud_scale}]",
        f"Precipitation: [{rain_scale}] {chance_of_rain}%",
    ]

    if full_details:
        msg.extend([
            "",
            "💧 *DETAILS*",
            f"Humidity: [{humidity_scale}] {humidity}%",
            f"UV Index: {uv} {uv_icon}",
            f"Air Quality: {aqi_desc}" if aqi_desc else "",
            "",
            "💨 *WIND & PRESSURE*",
            f"Power: [{wind_scale}] {wind_kph} km/h",
            f"Gusts: {gust_kph} km/h" if gust_kph != "N/A" else "",
            f"Pressure: {pressure_mb} hPa" if pressure_mb != "N/A" else "",
            "",
            "🌓 *ASTRONOMY*",
            f"🌅 {sunrise_24h} | 🌇 {sunset_24h}",
            f"Moon: {astro.get('moon_phase', 'N/A')} {MOON_EMOJIS.get(astro.get('moon_phase'), '🌙')}",
            alerts_section
        ])

    final_msg = "\n".join([line for line in msg if line is not None]).strip()

    keyboard = []
    
    # Details button
    if not full_details:
        more_callback = f"moretomorrow_{city}" if is_tomorrow else f"more_{city}"
        keyboard.append([InlineKeyboardButton("📖 Read More", callback_data=more_callback)])
    
    row1 = []
    if is_tomorrow:
        row1.append(InlineKeyboardButton("🔙 Today", callback_data=f"today_{city}"))
    else:
        row1.append(InlineKeyboardButton("📅 Tomorrow", callback_data=f"tomorrow_{city}"))
    keyboard.append(row1)
    
    chart_callback = f"charttomorrow_{city}" if is_tomorrow else f"chart_{city}"
    keyboard.append([
        InlineKeyboardButton("📈 24h Chart", callback_data=chart_callback),
        InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{city}")
    ])
    
    keyboard.append([
        InlineKeyboardButton("🔔 Subscribe to 7:00 AM forecast", callback_data=f"sub_{city}")
    ])
    
    return final_msg, InlineKeyboardMarkup(keyboard)


def get_help_message() -> str:
    return (
        "❓ *How to use the bot?*\n\n"
        "📍 *City:* Type any city name (e.g., `London`) to check current weather.\n"
        "🗺️ *Location:* Send your GPS location using the button below.\n"
        "🔔 *Subscription:* Type `/sub City` to receive daily forecasts at 7:00 AM.\n"
        "📈 *Charts:* Click the '24h Chart' button after searching for a city.\n\n"
        "🤖 I'm here to help you plan your day!"
    )

def get_sticker_message() -> str:
    return (
        "Cool sticker! 😍 I can't interpret them yet, "
        "but I'm an expert in weather.\n\n"
        "Type a city name or send your location to check the forecast! 🌤️"
    )

def get_unknown_command_message() -> str:
    return (
        "🤖 *Oops! I don't know this command.*\n\n"
        "Type /start to see the main menu, or just enter the name of the city "
        "you want to check the weather for."
    )
