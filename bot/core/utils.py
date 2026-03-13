def get_temp_emoji(temp):
    try:
        t = float(temp)
        if t < 0: return "❄️"
        if t < 10: return "☁️"
        if t < 20: return "🌤️"
        if t < 30: return "☀️"
        return "🔥"
    except: return "🌡️"

def get_feelslike_emoji(t):
    try:
        t = float(t)
        if t < 5: return "🥶"
        if t < 25: return "🌡️"
        return "🥵"
    except: return "🌡️"

def get_visual_scale(value, max_val=100, emoji="▫️", empty_char="—", alt_zero=None):
    try:
        val = float(value)
        steps = int(round((val / max_val) * 4))
        steps = max(0, min(4, steps))
        
        if steps == 0 and alt_zero:
            return f"{alt_zero} — — —"
        
        scale = [emoji] * steps + [empty_char] * (4 - steps)
        return " ".join(scale)
    except: return "— — — —"

def get_wind_emoji(speed):
    try:
        s = float(speed)
        if s < 10: return "🍃"
        if s < 30: return "🌬️"
        if s < 60: return "💨"
        return "🌪️"
    except: return "💨"

def get_uv_emoji(uv):
    try:
        u = float(uv)
        if u <= 2: return "✅"
        if u <= 5: return "🟡"
        if u <= 7: return "🟠"
        if u <= 10: return "🔴"
        return "🟣"
    except: return "☀️"

def normalize_city_name(city_name: str) -> str:
    if not city_name:
        return city_name
    mapping = str.maketrans(
        "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ",
        "acelnoszzACELNOSZZ"
    )
    return city_name.translate(mapping)

