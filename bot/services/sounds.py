"""
🔊 Sound effects service for the weather bot.

Sends .ogg audio files matching weather conditions or bot events.
Files are read from bot/sounds/ directory. Missing files are silently skipped.
"""

import os
import logging
from pathlib import Path
from telegram import Bot

logger = logging.getLogger(__name__)

# Absolute path to the sounds directory
SOUNDS_DIR = Path(__file__).parent.parent / "sounds"

# Weather condition keywords → sound file mapping
# Keys are lowercase substrings matched against condition text from the API
WEATHER_SOUND_MAP: dict[str, str] = {
    # Rain variants
    "drizzle":          "rain.ogg",
    "light rain":       "rain.ogg",
    "moderate rain":    "rain.ogg",
    "heavy rain":       "rain.ogg",
    "patchy rain":      "rain.ogg",
    "rain":             "rain.ogg",
    "sleet":            "rain.ogg",
    "freezing rain":    "rain.ogg",
    "ice pellets":      "rain.ogg",
    "light drizzle":    "rain.ogg",

    # Storm / severe
    "thundery":         "storm.ogg",
    "thunder":          "storm.ogg",
    "blizzard":         "storm.ogg",
    "heavy snow":       "storm.ogg",

    # Sunny / clear
    "sunny":            "sunny.ogg",
    "clear":            "sunny.ogg",
}

# Special event sounds (used directly by name)
EVENT_SOUNDS: dict[str, str] = {
    "subscribe":        "subscribe.ogg",
    "error":            "error.ogg",
}


def _get_sound_path(filename: str) -> Path | None:
    """Return Path to a sound file if it exists, else None."""
    path = SOUNDS_DIR / filename
    if path.exists() and path.is_file():
        return path
    logger.debug(f"Sound file not found, skipping: {path}")
    return None


def get_weather_sound(condition_text: str) -> Path | None:
    """
    Given a weather condition string (e.g. 'Heavy rain'),
    return the matching .ogg Path or None if no match / file missing.
    """
    condition_lower = condition_text.lower()
    for keyword, filename in WEATHER_SOUND_MAP.items():
        if keyword in condition_lower:
            return _get_sound_path(filename)
    return None


def get_event_sound(event: str) -> Path | None:
    """
    Return the .ogg Path for a named bot event ('subscribe', 'error', etc.)
    or None if no file exists.
    """
    filename = EVENT_SOUNDS.get(event)
    if not filename:
        return None
    return _get_sound_path(filename)


async def send_weather_sound(bot: Bot, chat_id: int, condition_text: str) -> bool:
    """
    Detect weather condition from text and send matching audio to chat.
    Returns True if a sound was sent, False otherwise.
    """
    sound_path = get_weather_sound(condition_text)
    if not sound_path:
        return False

    try:
        with open(sound_path, "rb") as audio_file:
            await bot.send_voice(
                chat_id=chat_id,
                voice=audio_file,
                disable_notification=True,   # silent — no push sound on top of this
            )
        logger.info(f"🔊 Sent weather sound '{sound_path.name}' to {chat_id}")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Could not send weather sound '{sound_path.name}': {e}")
        return False


async def send_event_sound(bot: Bot, chat_id: int, event: str) -> bool:
    """
    Send a named bot-event sound ('subscribe', 'error', etc.) to chat.
    Returns True if a sound was sent, False otherwise.
    """
    sound_path = get_event_sound(event)
    if not sound_path:
        return False

    try:
        with open(sound_path, "rb") as audio_file:
            await bot.send_voice(
                chat_id=chat_id,
                voice=audio_file,
                disable_notification=False,  # audible confirmation for user
            )
        logger.info(f"🔔 Sent event sound '{sound_path.name}' to {chat_id}")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Could not send event sound '{sound_path.name}': {e}")
        return False
