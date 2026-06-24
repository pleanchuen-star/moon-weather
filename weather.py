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
thai_time = datetime.now(ZoneInfo("Asia/Bangkok"))

def get_weather():
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": "Bangkok", "appid": API_KEY, "units": "metric"}
    )
    return r.json()

def build_embed(data):
    temp = round(data["main"]["temp"])
    feels = round(data["main"]["feels_like"])
    weather = data["weather"][0]["description"]

    return {
        "title": "🌤️ Live Weather Bangkok",
        "description": f"🕒 {datetime.now()}",
        "color": 0x3498db,
        "fields": [
            {"name": "🌡️ Temp", "value": f"{temp}°C", "inline": True},
            {"name": "🤔 Feels like", "value": f"{feels}°C", "inline": True},
            {"name": "☁️ Condition", "value": weather, "inline": False},
        ]
    }

def load_msg_id():
    try:
        with open("msg.json") as f:
            return json.load(f)["id"]
    except:
        return None

def save_msg_id(mid):
    with open("msg.json", "w") as f:
        json.dump({"id": mid}, f)

def send_or_edit(embed, msg_id):
    if msg_id:
        # EDIT (LIVE UPDATE)
        requests.patch(
            WEBHOOK_URL + f"/messages/{msg_id}",
            json={"embeds": [embed]}
        )
        return msg_id
    else:
        # FIRST POST
        r = requests.post(
            WEBHOOK_URL + "?wait=true",
            json={"embeds": [embed]}
        )
        return r.json()["id"]


# =========================
# LOOP (LIVE SYSTEM)
# =========================

while True:
    data = get_weather()
    embed = build_embed(data)

    msg_id = load_msg_id()
    new_id = send_or_edit(embed, msg_id)
    save_msg_id(new_id)

    print("updated:", new_id)

    time.sleep(300)  # 5 นาที
