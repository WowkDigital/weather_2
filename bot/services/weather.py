import requests
from bot.core.config import WEATHER_API_KEY

def fetch_weather_data(query: str, days: int = 1) -> dict:
    if not WEATHER_API_KEY:
        return {"error": "Weather API key is missing!"}
        
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={query}&days={days}&aqi=yes&alerts=yes"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get("error", {}).get("message", "API Error")
            # Translation of common errors
            if "No matching location found" in error_msg:
                return {"error": "📍 City not found. Please check the name."}
            return {"error": f"❌ Error: {error_msg}"}
            
        return data
    except Exception as e:
        return {"error": f"❌ Connection error: {str(e)}"}
