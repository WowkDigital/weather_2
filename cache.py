WEATHER_CACHE = {}  # Format: {city: {"data": data, "timestamp": timestamp}}
CHART_CACHE = {}    # Format: {city: {"buffer": bytes, "timestamp": timestamp}}

def invalidate_caches(city):
    if city in WEATHER_CACHE:
        del WEATHER_CACHE[city]
    if city in CHART_CACHE:
        del CHART_CACHE[city]
