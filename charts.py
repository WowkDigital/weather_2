import io
from datetime import datetime
import matplotlib.pyplot as plt

def generate_feelslike_chart(data: dict, city: str):
    forecast_days = data.get("forecast", {}).get("forecastday", [])
    if not forecast_days:
        return None
        
    all_hours = []
    sun_events = []
    for day in forecast_days:
        all_hours.extend(day.get("hour", []))
        date_str = day.get("date")
        astro = day.get("astro", {})
        if "sunrise" in astro and "sunset" in astro:
            try:
                sr = datetime.strptime(f"{date_str} {astro['sunrise']}", "%Y-%m-%d %I:%M %p")
                ss = datetime.strptime(f"{date_str} {astro['sunset']}", "%Y-%m-%d %I:%M %p")
                sun_events.append(("🌅 Wschód", sr, "#ffea00"))
                sun_events.append(("🌇 Zachód", ss, "#ff5500"))
            except Exception:
                pass
    
    local_time_str = data.get("location", {}).get("localtime", "")
    try:
        current_time = datetime.strptime(local_time_str, "%Y-%m-%d %H:%M")
    except:
        current_time = datetime.now()
        
    relevant_hours = [h for h in all_hours if datetime.strptime(h["time"], "%Y-%m-%d %H:%M") >= current_time][:24]
    
    if not relevant_hours:
        relevant_hours = all_hours[:24]
        
    times = []
    temps = []
    for h in relevant_hours:
        time_part = h["time"].split(" ")[1]
        times.append(time_part)
        temps.append(h["feelslike_c"])
        
    plt.figure(figsize=(10, 5))
    plt.plot(times, temps, marker='o', linestyle='-', color='#00d2ff', linewidth=3, markersize=8)
    
    y_min, y_max = min(temps), max(temps)
    y_range = y_max - y_min if y_max > y_min else 1.0
    
    for i, (time_str, temp) in enumerate(zip(times, temps)):
        if i % 2 == 0:
            plt.annotate(f"{temp}°", (time_str, temp), textcoords="offset points", xytext=(0,10), ha='center', color='white', fontsize=10)

    for label, dt, color in sun_events:
        for i in range(len(relevant_hours) - 1):
            t1 = datetime.strptime(relevant_hours[i]["time"], "%Y-%m-%d %H:%M")
            t2 = datetime.strptime(relevant_hours[i+1]["time"], "%Y-%m-%d %H:%M")
            if t1 <= dt <= t2:
                fraction = (dt - t1).total_seconds() / (t2 - t1).total_seconds()
                pos = i + fraction
                plt.axvline(x=pos, color=color, linestyle='--', alpha=0.8, linewidth=2)
                plt.text(pos + 0.2, y_min + y_range * 0.1, f"{label}\n{dt.strftime('%H:%M')}", color=color, fontsize=9, va='bottom')
                break

    plt.title(f"Temperatura odczuwalna (24h) - {city}", fontsize=16, color='white', fontweight='bold', pad=20)
    plt.xlabel("Godzina", fontsize=12, color='white', labelpad=10)
    plt.ylabel("Temperatura (°C)", fontsize=12, color='white', labelpad=10)
    
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    plt.grid(True, linestyle='--', alpha=0.2, color='white')
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['left'].set_color('white')
    
    plt.gcf().set_facecolor('#1a1a1a')
    plt.gca().set_facecolor('#1a1a1a')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, facecolor='#1a1a1a')
    buf.seek(0)
    plt.close()
    return buf
