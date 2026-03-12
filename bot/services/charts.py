import io
from datetime import datetime
import matplotlib.pyplot as plt

def generate_feelslike_chart(data: dict, city: str, day_index: int = 0):
    forecast_days = data.get("forecast", {}).get("forecastday", [])
    if not forecast_days or len(forecast_days) <= day_index:
        return None
        
    all_hours = []
    sun_events = []
    
    target_day = forecast_days[day_index]
    relevant_hours = target_day.get("hour", [])[:24]
    target_date = target_day.get("date", "")

    # Astro for sun events
    astro = target_day.get("astro", {})
    if "sunrise" in astro and "sunset" in astro:
        try:
            sr = datetime.strptime(f"{target_date} {astro['sunrise']}", "%Y-%m-%d %I:%M %p")
            ss = datetime.strptime(f"{target_date} {astro['sunset']}", "%Y-%m-%d %I:%M %p")
            sun_events.append(("Sunrise", sr, "#ffea00"))
            sun_events.append(("Sunset", ss, "#ff5500"))
        except Exception:
            pass
        
    times = []
    temps = []
    precips = []
    for h in relevant_hours:
        time_part = h["time"].split(" ")[1]
        times.append(time_part)
        temps.append(h["feelslike_c"])
        precips.append(h.get("precip_mm", 0))
        
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Precipitation (bars) - only if forecasted
    has_precip = any(p > 0 for p in precips)
    if has_precip:
        ax2 = ax1.twinx()
        ax2.bar(times, precips, color='#0078ff', alpha=0.4, label='Precipitation (mm)', width=0.6)
        ax2.set_ylabel('Precipitation (mm)', color='#0078ff', fontsize=12, labelpad=10)
        ax2.tick_params(axis='y', labelcolor='#0078ff')
        ax2.grid(False)
        
        # Scaling precipitation axis so bars don't overlap temperature line too much
        max_precip = max(precips)
        ax2.set_ylim(0, max_precip * 3 if max_precip > 0 else 1)
        
        # Add labels over bars if significant
        for i, p in enumerate(precips):
            if p > 0.1:
                ax2.text(i, p + 0.05, f"{p}", ha='center', va='bottom', color='#0078ff', fontsize=8, fontweight='bold')

    # Temperature (line)
    ax1.plot(times, temps, marker='o', linestyle='-', color='#00d2ff', linewidth=3, markersize=8, zorder=10)
    
    y_min, y_max = min(temps), max(temps)
    y_range = y_max - y_min if y_max > y_min else 1.0
    
    for i, (time_str, temp) in enumerate(zip(times, temps)):
        if i % 2 == 0:
            ax1.annotate(f"{temp}°", (time_str, temp), textcoords="offset points", xytext=(0,10), ha='center', color='white', fontsize=10, fontweight='bold')

    # Solar events
    for label, dt, color in sun_events:
        for i in range(len(relevant_hours) - 1):
            t1 = datetime.strptime(relevant_hours[i]["time"], "%Y-%m-%d %H:%M")
            t2 = datetime.strptime(relevant_hours[i+1]["time"], "%Y-%m-%d %H:%M")
            if t1 <= dt <= t2:
                fraction = (dt - t1).total_seconds() / (t2 - t1).total_seconds()
                pos = i + fraction
                ax1.axvline(x=pos, color=color, linestyle='--', alpha=0.8, linewidth=2)
                ax1.text(pos + 0.2, y_min + y_range * 0.1, f"{label}\n{dt.strftime('%H:%M')}", color=color, fontsize=9, va='bottom', fontweight='bold')
                break

    chart_title = f"24h Forecast: {city} ({target_date})"
    ax1.set_title(chart_title, fontsize=16, color='white', fontweight='bold', pad=25)
    ax1.set_xlabel("Hour", fontsize=12, color='white', labelpad=10)
    ax1.set_ylabel("Feels Like Temp (°C)", fontsize=12, color='white', labelpad=10)
    
    ax1.set_xticks(range(len(times)))
    ax1.set_xticklabels(times, rotation=45, color='white')
    ax1.tick_params(axis='y', labelcolor='white')
    ax1.grid(True, linestyle='--', alpha=0.2, color='white')
    
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_color('white')
    ax1.spines['left'].set_color('white')
    
    if has_precip:
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_color('#0078ff')
        ax2.spines['left'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)

    fig.patch.set_facecolor('#1a1a1a')
    ax1.set_facecolor('#1a1a1a')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, facecolor='#1a1a1a')
    buf.seek(0)
    plt.close()
    return buf
