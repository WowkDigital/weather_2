from datetime import datetime
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import MOON_EMOJIS
from utils import get_temp_emoji, get_feelslike_emoji, get_visual_scale, get_wind_emoji, get_uv_emoji

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
        clouds = day.get("cloud", 50)
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
            if val <= 3: aqi_desc = "Dobra 🟢"
            elif val <= 6: aqi_desc = "Średnia 🟡"
            else: aqi_desc = "Zła 🔴"
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

    final_msg = "\n".join([line for line in msg if line is not None]).strip()

    keyboard = []
    if is_tomorrow:
        keyboard.append([InlineKeyboardButton("🔙 Dzisiaj", callback_data=f"today_{city}")])
    else:
        keyboard.append([InlineKeyboardButton("📅 Jutro", callback_data=f"tomorrow_{city}")])
    
    chart_callback = f"charttomorrow_{city}" if is_tomorrow else f"chart_{city}"
    keyboard.append([
        InlineKeyboardButton("📈 Wykres 24h", callback_data=chart_callback),
        InlineKeyboardButton("🔄 Odśwież", callback_data=f"refresh_{city}")
    ])
    
    keyboard.append([
        InlineKeyboardButton("🔔 Subskrybuj prognozę o 7:00", callback_data=f"sub_{city}")
    ])
    
    return final_msg, InlineKeyboardMarkup(keyboard)
