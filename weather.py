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
    "🌏 ภาคเหนือ": {
        "เชียงใหม่": "Chiang Mai",
        "เชียงราย": "Chiang Rai",
        "พิษณุโลก": "Phitsanulok",
    },
    "🌾 ภาคอีสาน": {
        "ขอนแก่น": "Khon Kaen",
        "นครราชสีมา": "Nakhon Ratchasima",
    },
    "🏙️ ภาคกลาง": {
        "กรุงเทพฯ": "Bangkok",
        "นนทบุรี": "Nonthaburi",
    },
    "🌊 ภาคตะวันออก": {
        "ชลบุรี": "Chon Buri",
        "ระยอง": "Rayong",
    },
    "🌴 ภาคใต้": {
        "ภูเก็ต": "Phuket",
        "สงขลา": "Songkhla",
    }
}


# =========================
# WEATHER FETCH
# =========================

def fetch_weather(city):
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
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

            # icon
            if temp >= 35:
                icon = "🔥"
            elif temp >= 30:
                icon = "🌤️"
            else:
                icon = "🌦️"

            block.append(
                f"**{name}** {icon}\n"
                f"🌡️ {temp}°C | 🤔 {feels}°C\n"
                f"☁️ {desc}"
            )

        fields.append({
            "name": region,
            "value": "\n\n".join(block),
            "inline": False
        })

    return {
        "title": "🌤️ Live Weather Thailand Dashboard",
        "description": f"🕒 {datetime.now(thai_tz).strftime('%d/%m/%Y %H:%M')}",
        "color": 0x3498db,
        "fields": fields
    }


# =========================
# DISCORD MESSAGE CONTROL
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
# MAIN LOOP
# =========================

while True:
    embed = build_embed()

    msg_id = load_msg_id()
    new_id = send_or_edit(embed, msg_id)
    save_msg_id(new_id)

    print("updated:", new_id)

    time.sleep(300)  # 5 นาที
