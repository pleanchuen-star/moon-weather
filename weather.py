import requests
import time
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================
# CONFIG
# =========================

API_KEY = "3e0a7d09d6908c0092ec0a188a91de31"
WEBHOOK_URL = "https://discord.com/api/webhooks/1517002604025217049/wxBMAicuP1W6pO2Tp3hOy05nxQZAXVIZREWJRBFPYsdmTzQf8rw3Yku0LWZgJ0HTRuDN"
thai_tz = ZoneInfo("Asia/Bangkok")

# =========================
# REGIONS
# =========================

REGIONS = {
    "ภาคเหนือ": {
        "เชียงใหม่": "Chiang Mai",
        "พิษณุโลก": "Phitsanulok",
    },
    "ภาคอีสาน": {
        "ขอนแก่น": "Khon Kaen",
        "นครราชสีมา": "Nakhon Ratchasima",
    },
    "ภาคกลาง": {
        "กรุงเทพฯ": "Bangkok",
        "นนทบุรี": "Nonthaburi",
    },
    "ภาคตะวันออก": {
        "ชลบุรี": "Chon Buri",
    },
    "ภาคใต้": {
        "ภูเก็ต": "Phuket",
    }
}

# =========================
# API FUNCTIONS
# =========================

def fetch_weather(city):
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric",
                "lang": "th"
            },
            timeout=10
        )
        return r.json()
    except:
        return None


def fetch_air_pollution(lat, lon):
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/air_pollution",
            params={
                "lat": lat,
                "lon": lon,
                "appid": API_KEY
            },
            timeout=10
        )
        return r.json()
    except:
        return None


def fetch_forecast(city):
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=10
        )
        return r.json()
    except:
        return None

# =========================
# EMBED BUILDER
# =========================

def build_embed():
    fields = []

    for region, cities in REGIONS.items():

        block = []

        for name, city in cities.items():

            data = fetch_weather(city)

            if not data or "main" not in data:
                continue

            temp = round(data["main"]["temp"])
            feels = round(data["main"]["feels_like"])
            desc = data["weather"][0]["description"]

            lat = data["coord"]["lat"]
            lon = data["coord"]["lon"]

            # PM2.5 / AQI
            pm25 = "-"
            aqi = "-"

            air = fetch_air_pollution(lat, lon)

            if air and "list" in air:
                pm25 = round(air["list"][0]["components"]["pm2_5"], 1)
                aqi = air["list"][0]["main"]["aqi"]

            # Rain forecast
            rain = "ไม่มีฝน"

            forecast = fetch_forecast(city)

            if forecast and "list" in forecast:
                for item in forecast["list"][:3]:
                    if item.get("pop", 0) >= 0.4:
                        rain = "มีโอกาสฝน"
                        break

            # Icon
            if temp >= 35:
                icon = "🔥"
            elif temp >= 30:
                icon = "🌤️"
            else:
                icon = "🌦️"

            block.append(
                f"**{name}** {icon}\n"
                f"🌡️ {temp}°C | 🤔 {feels}°C\n"
                f"☁️ {desc}\n"
                f"🌫️ PM2.5: {pm25}\n"
                f"📊 AQI: {aqi}\n"
                f"🌧️ {rain}"
            )

        fields.append({
            "name": region,
            "value": "\n\n".join(block) if block else "-",
            "inline": False
        })

    return {
        "title": "🌦️ รายงานสภาพอากาศประเทศไทย",
        "description": f"🕒 อัปเดตล่าสุด {datetime.now(thai_tz).strftime('%d/%m/%Y %H:%M')}",
        "color": 0x3498DB,
        "fields": fields
    }

# =========================
# DISCORD
# =========================

def load_msg_id():
    try:
        with open("msg.json", "r") as f:
            return json.load(f)["id"]
    except:
        return None


def save_msg_id(mid):
    with open("msg.json", "w") as f:
        json.dump({"id": mid}, f)


def send_or_edit(embed, msg_id):

    if msg_id:
        requests.patch(
            WEBHOOK_URL + f"/messages/{msg_id}",
            json={"embeds": [embed]}
        )
        return msg_id

    r = requests.post(
        WEBHOOK_URL + "?wait=true",
        json={"embeds": [embed]}
    )

    return r.json()["id"]

# =========================
# MAIN LOOP
# =========================

while True:

    try:
        embed = build_embed()

        msg_id = load_msg_id()

        new_id = send_or_edit(embed, msg_id)

        save_msg_id(new_id)

        print(f"[{datetime.now(thai_tz)}] Updated: {new_id}")

    except Exception as e:
        print("ERROR:", e)

    time.sleep(300)
