import requests
from datetime import datetime

# =========================
# CONFIG
# =========================

API_KEY = "3e0a7d09d6908c0092ec0a188a91de31"
WEBHOOK_URL = "https://discord.com/api/webhooks/1517002604025217049/wxBMAicuP1W6pO2Tp3hOy05nxQZAXVIZREWJRBFPYsdmTzQf8rw3Yku0LWZgJ0HTRuDN"

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

highest_feels = -999
highest_feels_city = ""

highest_pm25 = -999
highest_pm25_city = ""

highest_rain = -1
highest_rain_city = ""

umbrella_list = []

message = (
    "🇹🇭 **รายงานอากาศประเทศไทย**\n"
    f"{datetime.now().strftime('%d/%m/%Y')} | "
    f"{datetime.now().strftime('%H:%M')} น.\n\n"
)

for region, cities in REGIONS.items():

    message += "──────────────\n\n"
    message += f"**{region}**\n\n"

    for thai_name, city in cities.items():

        try:
            weather = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "appid": API_KEY,
                    "units": "metric"
                },
                timeout=10
            )

            weather.raise_for_status()
            weather = weather.json()

            feels = round(weather["main"]["feels_like"])
            lat = weather["coord"]["lat"]
            lon = weather["coord"]["lon"]

            # -----------------
            # PM2.5
            # -----------------
            pm25 = "-"

            try:
                air = requests.get(
                    "https://api.openweathermap.org/data/2.5/air_pollution",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": API_KEY
                    },
                    timeout=10
                )

                air.raise_for_status()
                air = air.json()

                pm25 = round(air["list"][0]["components"]["pm2_5"], 1)

            except Exception as e:
                print("PM2.5 error:", city, e)

            # -----------------
            # Rain Chance
            # -----------------
            rain = 0

            try:
                forecast = requests.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": API_KEY,
                        "units": "metric"
                    },
                    timeout=10
                )

                forecast.raise_for_status()
                forecast = forecast.json()

                rain = int(
                    max(item.get("pop", 0) for item in forecast["list"][:5]) * 100
                )

            except Exception as e:
                print("Rain error:", city, e)

            # -----------------
            # UV (FIXED)
            # -----------------
            uv = "-"

            try:
                uv_data = requests.get(
                    "https://api.openweathermap.org/data/2.5/uvi",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": API_KEY
                    },
                    timeout=10
                )

                uv_data.raise_for_status()
                uv = round(uv_data.json()["value"], 1)

            except Exception as e:
                print("UV error:", city, e)

            # -----------------
            # Summary tracking
            # -----------------
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

            # -----------------
            # Output
            # -----------------
            message += (
                f"{thai_name}\n"
                f"🌧️ ฝน {rain}%\n"
                f"🌡️ Feels {feels}°C\n"
                f"😷 PM2.5 {pm25}\n"
                f"☀️ UV {uv}\n\n"
            )

        except Exception as e:
            print(f"{city}: {e}")
            message += f"{thai_name}\n❌ ไม่สามารถดึงข้อมูลได้\n\n"

# =====================
# SUMMARY
# =====================

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
if len(message) > 1900:
    message = message[:1900] + "\n...(ตัดข้อความบางส่วน)"

print(message)

# =====================
# SEND DISCORD
# =====================

MESSAGE_ID = "1517770437281448087"

edit_url = f"{WEBHOOK_URL}/messages/{MESSAGE_ID}"

response = requests.patch(
    edit_url,
    json={"content": message},
    timeout=30
)

if response.status_code in [200, 204]:

    print("✅ อัปเดตสำเร็จ")

    # แจ้งเตือน
    requests.post(
        WEBHOOK_URL,
        json={
            "content": "🌦️ รายงานอากาศประจำวันอัปเดตแล้ว"
        },
        timeout=30
    )

else:
    print("❌ Error")
    print(response.text)