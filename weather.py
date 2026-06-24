import requests
from datetime import datetime
from zoneinfo import ZoneInfo
thai_time = datetime.now(ZoneInfo("Asia/Bangkok"))

# =========================
# CONFIG
# =========================

API_KEY = "3e0a7d09d6908c0092ec0a188a91de31"
WEBHOOK_URL = "https://discord.com/api/webhooks/1517002604025217049/wxBMAicuP1W6pO2Tp3hOy05nxQZAXVIZREWJRBFPYsdmTzQf8rw3Yku0LWZgJ0HTRuDN"

import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================
# CONFIG
# =========================

API_KEY = "YOUR_API_KEY"
WEBHOOK_URL = "YOUR_WEBHOOK_URL"

MESSAGE_ID = "1517770437281448087"

REGIONS = {
    "ภาคเหนือ": {
        "เชียงใหม่": "Chiang Mai",
        "พิษณุโลก": "Phitsanulok",
    },
    "ภาคตะวันออกเฉียงเหนือ": {
        "ขอนแก่น": "Khon Kaen",
        "นครราชสีมา": "Nakhon Ratchasima",
    },
    "ภาคกลาง": {
        "กรุงเทพฯ": "Bangkok",
    },
    "ภาคตะวันออก": {
        "ชลบุรี": "Chon Buri",
    },
    "ภาคใต้": {
        "ภูเก็ต": "Phuket",
    },
}

# =========================
# DATA
# =========================

highest_feels = -999
highest_feels_city = ""

highest_pm25 = -999
highest_pm25_city = ""

highest_rain = -1
highest_rain_city = ""

umbrella_list = []

thai_time = datetime.now(ZoneInfo("Asia/Bangkok"))

message = (
    "🇹🇭 **รายงานอากาศประเทศไทย**\n"
    f"{thai_time.strftime('%d/%m/%Y')} | {thai_time.strftime('%H:%M')} น.\n\n"
)

# =========================
# FETCH DATA
# =========================

for region, cities in REGIONS.items():

    message += "──────────────\n\n"
    message += f"**{region}**\n\n"

    for thai_name, city in cities.items():

        try:
            weather = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": API_KEY, "units": "metric"},
                timeout=10
            ).json()

            feels = round(weather["main"]["feels_like"])
            lat = weather["coord"]["lat"]
            lon = weather["coord"]["lon"]

            # -------- PM2.5 --------
            pm25 = "-"

            try:
                air = requests.get(
                    "https://api.openweathermap.org/data/2.5/air_pollution",
                    params={"lat": lat, "lon": lon, "appid": API_KEY},
                    timeout=10
                ).json()

                pm25 = round(air["list"][0]["components"]["pm2_5"], 1)
            except:
                pass

            # -------- Rain --------
            rain = 0

            try:
                forecast = requests.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"},
                    timeout=10
                ).json()

                rain = int(
                    max(item.get("pop", 0) for item in forecast["list"][:5]) * 100
                )
            except:
                pass

            # -------- UV --------
            uv = "-"

            try:
                uv_data = requests.get(
                    "https://api.openweathermap.org/data/2.5/uvi",
                    params={"lat": lat, "lon": lon, "appid": API_KEY},
                    timeout=10
                ).json()

                uv = round(uv_data["value"], 1)
            except:
                pass

            # -------- summary --------
            if feels > highest_feels:
                highest_feels = feels
                highest_feels_city = thai_name

            if rain > highest_rain:
                highest_rain = rain
                highest_rain_city = thai_name

            if pm25 != "-" and pm25 > highest_pm25:
                highest_pm25 = pm25
                highest_pm25_city = thai_name

            if rain >= 70:
                umbrella_list.append(thai_name)

            # -------- message --------
            message += (
                f"{thai_name}\n"
                f"🌧️ ฝน {rain}%\n"
                f"🌡️ Feels {feels}°C\n"
                f"😷 PM2.5 {pm25}\n"
                f"☀️ UV {uv}\n\n"
            )

        except:
            message += f"{thai_name}\n❌ ไม่สามารถดึงข้อมูลได้\n\n"

# =========================
# SUMMARY
# =========================

message += "──────────────\n\n"
message += "**สรุปประเทศ**\n\n"

message += f"☔ ฝนมากสุด : {highest_rain_city} {highest_rain}%\n"
message += f"🌡️ Feels สูงสุด : {highest_feels_city} {highest_feels}°C\n"

if highest_pm25_city:
    message += f"😷 PM2.5 สูงสุด : {highest_pm25_city} {highest_pm25}\n"

if umbrella_list:
    message += "\n🌧️ ควรพกร่ม\n"
    for city in umbrella_list:
        message += f"• {city}\n"

# limit Discord
message = message[:1900]

print(message)

# =========================
# DISCORD CLEAN SEND
# =========================

try:
    # ลบข้อความเก่า (ถ้ามี)
    requests.delete(f"{WEBHOOK_URL}/messages/{MESSAGE_ID}")
except:
    pass

# ส่งใหม่ (สะอาดสุด)
response = requests.post(
    WEBHOOK_URL,
    json={"content": message},
    timeout=30
)

if response.status_code in [200, 204]:
    print("✅ ส่งอัปเดตสำเร็จ (clean mode)")
else:
    print("❌ Error:", response.text)
