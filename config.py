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
    "CAACAgIAAxkBAAEL_m9mIFGZ9-G9X2_3p6S3S7uYn_Q", # Sun
    "CAACAgIAAxkBAAEL_m1mIFGNo6_7S2-Uu7_n_S_U",    # Cloud
    "CAACAgIAAxkBAAEL_mtmIFF8G9-G9X2_3p6S3S7uYn_Q", # Rain
    "CAACAgIAAxkBAAEL_mlmIFFoG9-G9X2_3p6S3S7uYn_Q"  # Storm
]
