# Simple in-memory cache for charts
CHART_CACHE = {}

def invalidate_caches(city: str):
    """Remove records for a specific city from cache"""
    keys_to_remove = [k for k in CHART_CACHE.keys() if k.startswith(city)]
    for k in keys_to_remove:
        del CHART_CACHE[k]
