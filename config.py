import os
from dotenv import load_dotenv

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

CACHE_EXPIRATION_SECONDS = 900  # 15 minutes

# Naklejki pogodowe (używamy publicznych i sprawdzonych ID)
WEATHER_STICKERS = [
    "CAACAgQAAxkBAAFEiEhpse1isLmD22KWsoX5Sqv8eR_nVwAC9xcAAiKWKVNtiuPkDDMfJToE", # Sun
    "CAACAgQAAxkBAAFEiEhpse1isLmD22KWsoX5Sqv8eR_nVwAC9xcAAiKWKVNtiuPkDDMfJToE",    # Cloud
    "CAACAgQAAxkBAAFEiEhpse1isLmD22KWsoX5Sqv8eR_nVwAC9xcAAiKWKVNtiuPkDDMfJToE", # Rain
    "CAACAgQAAxkBAAFEiEhpse1isLmD22KWsoX5Sqv8eR_nVwAC9xcAAiKWKVNtiuPkDDMfJToE"  # Storm
    
]
