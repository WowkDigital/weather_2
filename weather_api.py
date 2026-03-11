import time
import requests
from config import WEATHER_API_KEY, CACHE_EXPIRATION_SECONDS
from cache import WEATHER_CACHE, CHART_CACHE

def fetch_weather_data(city: str, days: int = 1) -> dict:
    if not WEATHER_API_KEY:
        return {"error": "⚠️ Brak klucza API. Skonfiguruj zmienną WEATHER_API_KEY."}
    
    city_map = {
        "Wrocław": "Wroclaw",
        "Kraków": "Krakow",
        "Gdańsk": "Gdansk",
        "Poznań": "Poznan",
        "Łódź": "Lodz"
    }
    query_city = city_map.get(city, city)
    
    current_time = time.time()
    if city in WEATHER_CACHE:
        cached = WEATHER_CACHE[city]
        if current_time - cached["timestamp"] < CACHE_EXPIRATION_SECONDS:
            return cached["data"]
            
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
        
        if "error" not in data:
            WEATHER_CACHE[city] = {"data": data, "timestamp": time.time()}
            if city in CHART_CACHE:
                del CHART_CACHE[city]
                
        return data
    except Exception:
        return {"error": f"❌ Błąd sieci przy pobieraniu danych dla {city}."}
