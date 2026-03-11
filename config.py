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

# Naklejki pogodowe (IDs z przykładowej paczki Telegram/Standardowej)
WEATHER_STICKERS = [
    "CAACAgIAAxkBAAEL2GtmHM7eW_9f_1S_U7f0W6_n_U", # Słońce
    "CAACAgIAAxkBAAEL2GxmHM7oV_2f_2S_U7f0W6_n_U", # Chmurka
    "CAACAgIAAxkBAAEL2G1mHM7zX_3f_3S_U7f0W6_n_U", # Deszcz
    "CAACAgEAAxkBAAMZZZqWv_h_2_f_1S_U7f0W6_n_U"    # Piorun
]
