import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import os

# =========================
# CONFIG
# =========================

API_KEY = "3e0a7d09d6908c0092ec0a188a91de31"
WEBHOOK_URL = "https://discord.com/api/webhooks/1517002604025217049/wxBMAicuP1W6pO2Tp3hOy05nxQZAXVIZREWJRBFPYsdmTzQf8rw3Yku0LWZgJ0HTRuDN"
thai_time = datetime.now(ZoneInfo("Asia/Bangkok"))

REGIONS = {
    "ภาคเหนือ": {"เชียงใหม่": "Chiang Mai", "พิษณุโลก": "Phitsanulok"},
    "ภาคอีสาน": {"ขอนแก่น": "Khon Kaen", "นครราชสีมา": "Nakhon Ratchasima"},
    "ภาคกลาง": {"กรุงเทพฯ": "Bangkok"},
    "ภาคตะวันออก": {"ชลบุรี": "Chon Buri"},
    "ภาคใต้": {"ภูเก็ต": "Phuket"},
}


def safe_get(url, params):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Request error: {url} -> {e}")
        return None


highest_feels = -999
highest_feels_city = ""

highest_pm25 = -999
highest_pm25_city = ""

highest_rain = -1
highest_rain_city = ""

umbrella_list = []
fields = []


for region, cities in REGIONS.items():
    block = []

    for name, city in cities.items():

        weather = safe_get(
            "https://api.openweathermap.org/data/2.5/weather",
            {"q": city, "appid": API_KEY, "units": "metric"}
        )

        if not weather:
            continue

        feels = round(weather["main"].get("feels_like", 0))
        lat, lon = weather["coord"]["lat"], weather["coord"]["lon"]

        air = safe_get(
            "https://api.openweathermap.org/data/2.5/air_pollution",
            {"lat": lat, "lon": lon, "appid": API_KEY}
        )

        pm25 = None
        if air:
            try:
                pm25 = float(air["list"][0]["components"]["pm2_5"])
            except:
                pm25 = None

        forecast = safe_get(
            "https://api.openweathermap.org/data/2.5/forecast",
            {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        )

        rain = 0
        if forecast:
            try:
                rain = int(
                    max(item.get("pop", 0) for item in forecast["list"][:5]) * 100
                )
            except:
                rain = 0

        # tracking max values
        if feels > highest_feels:
            highest_feels = feels
            highest_feels_city = name

        if rain > highest_rain:
            highest_rain = rain
            highest_rain_city = name

        if pm25 is not None and pm25 > highest_pm25:
            highest_pm25 = pm25
            highest_pm25_city = name

        if rain >= 70:
            umbrella_list.append(name)

        pm25_display = f"{pm25:.1f}" if pm25 is not None else "-"

        block.append(
            f"**{name}**\n🌧️ {rain}% 🌡️ {feels}°C 😷 {pm25_display}"
        )

    fields.append({
        "name": f"📍 {region}",
        "value": "\n\n".join(block),
        "inline": False
    })


def color():
    if highest_rain >= 70:
        return 0x2c3e50
    if highest_feels >= 35:
        return 0xe74c3c
    if highest_rain >= 30:
        return 0x3498db
    return 0x2ecc71


summary = (
    f"🌧️ ฝนมากสุด: {highest_rain_city} ({highest_rain}%)\n"
    f"🌡️ ร้อนสุด: {highest_feels_city} ({highest_feels}°C)\n"
)

if highest_pm25_city:
    summary += f"😷 PM2.5 แย่สุด: {highest_pm25_city} ({highest_pm25:.1f})\n"

if umbrella_list:
    summary += "\n☔ ควรพกร่ม:\n" + "\n".join(f"• {c}" for c in umbrella_list)


fields.append({
    "name": "📊 Summary",
    "value": summary,
    "inline": False
})


embed = {
    "title": "🇹🇭 Weather Dashboard PRO",
    "description": f"🕒 {thai_time:%d/%m/%Y %H:%M}",
    "color": color(),
    "fields": fields,
    "footer": {"text": "Weather Bot"}
}


requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=30)

print("✅ DONE")
