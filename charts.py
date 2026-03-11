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
                sun_events.append(("Wschód", sr, "#ffea00"))
                sun_events.append(("Zachód", ss, "#ff5500"))
            except Exception:
                pass
    
    relevant_hours = forecast_days[0].get("hour", [])[:24]
    target_date = forecast_days[0].get("date", "")
        
    times = []
    temps = []
    precips = []
    for h in relevant_hours:
        time_part = h["time"].split(" ")[1]
        times.append(time_part)
        temps.append(h["feelslike_c"])
        precips.append(h.get("precip_mm", 0))
        
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Opady (słupki) - tylko jeśli są prognozowane
    has_precip = any(p > 0 for p in precips)
    if has_precip:
        ax2 = ax1.twinx()
        ax2.bar(times, precips, color='#0078ff', alpha=0.4, label='Opady (mm)', width=0.6)
        ax2.set_ylabel('Opady (mm)', color='#0078ff', fontsize=12, labelpad=10)
        ax2.tick_params(axis='y', labelcolor='#0078ff')
        ax2.grid(False)
        # Skalowanie osi opadów, aby słupki nie zasłaniały całkowicie wykresu temperatury
        max_precip = max(precips)
        ax2.set_ylim(0, max_precip * 3 if max_precip > 0 else 1)
        # Dodanie etykiet nad słupkami jeśli opad jest istotny
        for i, p in enumerate(precips):
            if p > 0.1:
                ax2.text(i, p + 0.05, f"{p}", ha='center', va='bottom', color='#0078ff', fontsize=8, fontweight='bold')

    # Temperatura (linia)
    ax1.plot(times, temps, marker='o', linestyle='-', color='#00d2ff', linewidth=3, markersize=8, zorder=10)
    
    y_min, y_max = min(temps), max(temps)
    y_range = y_max - y_min if y_max > y_min else 1.0
    
    for i, (time_str, temp) in enumerate(zip(times, temps)):
        if i % 2 == 0:
            ax1.annotate(f"{temp}°", (time_str, temp), textcoords="offset points", xytext=(0,10), ha='center', color='white', fontsize=10, fontweight='bold')

    # Zdarzenia słoneczne
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

    chart_title = f"Prognoza 24h: {city} ({target_date})"
    ax1.set_title(chart_title, fontsize=16, color='white', fontweight='bold', pad=25)
    ax1.set_xlabel("Godzina", fontsize=12, color='white', labelpad=10)
    ax1.set_ylabel("Temperatura odczuwalna (°C)", fontsize=12, color='white', labelpad=10)
    
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
