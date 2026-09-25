import json
import datetime
from datetime import timedelta

def generate_route_flights(origin_code, dest_code, outbound_date, inbound_date):
    """
    主要航空会社の最新相場と具体空港名（KIX/ITM/HND/NRT/OKA/FUK/CTS）に基づいたデータを構築
    """
    route_configs = {
        "OSA-OKA": {
            "name": "大阪 (関空・伊丹) ➔ 沖縄 (那覇)",
            "airlines": [
                {"name": "Peach", "out_apt": "関空 (KIX) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 関空 (KIX)", "out_times": ["07:15–09:25", "11:30–13:40", "15:20–17:30"], "base": 8200},
                {"name": "JAL", "out_apt": "伊丹 (ITM) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 伊丹 (ITM)", "out_times": ["08:35–10:45", "14:10–16:20"], "base": 15800},
                {"name": "ANA", "out_apt": "伊丹 (ITM) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 伊丹 (ITM)", "out_times": ["09:50–12:00", "16:45–18:55"], "base": 16200},
                {"name": "Jetstar", "out_apt": "関空 (KIX) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 関空 (KIX)", "out_times": ["06:40–08:50", "13:00–15:10"], "base": 7800}
            ]
        },
        "TYO-OKA": {
            "name": "東京 (羽田・成田) ➔ 沖縄 (那覇)",
            "airlines": [
                {"name": "ANA", "out_apt": "羽田 (HND) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 羽田 (HND)", "out_times": ["06:20–09:00", "10:30–13:15", "15:00–17:45"], "base": 17800},
                {"name": "JAL", "out_apt": "羽田 (HND) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 羽田 (HND)", "out_times": ["07:30–10:15", "12:15–15:00", "16:30–19:15"], "base": 18200},
                {"name": "Peach", "out_apt": "成田 (NRT) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 成田 (NRT)", "out_times": ["08:10–11:00", "14:25–17:15"], "base": 9800},
                {"name": "Skymark", "out_apt": "羽田 (HND) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 羽田 (HND)", "out_times": ["09:10–12:00", "18:00–20:50"], "base": 12500}
            ]
        },
        "TYO-FUK": {
            "name": "東京 (羽田・成田) ➔ 福岡 (FUK)",
            "airlines": [
                {"name": "ANA", "out_apt": "羽田 (HND) ➔ 福岡 (FUK)", "in_apt": "福岡 (FUK) ➔ 羽田 (HND)", "out_times": ["07:00–08:55", "11:00–12:55", "17:30–19:25"], "base": 14500},
                {"name": "JAL", "out_apt": "羽田 (HND) ➔ 福岡 (FUK)", "in_apt": "福岡 (FUK) ➔ 羽田 (HND)", "out_times": ["08:00–09:55", "13:00–14:55", "18:30–20:25"], "base": 14800},
                {"name": "StarFlyer", "out_apt": "羽田 (HND) ➔ 福岡 (FUK)", "in_apt": "福岡 (FUK) ➔ 羽田 (HND)", "out_times": ["09:30–11:25", "15:15–17:10"], "base": 12800}
            ]
        },
        "TYO-CTS": {
            "name": "東京 (羽田・成田) ➔ 札幌 (新千歳)",
            "airlines": [
                {"name": "ANA", "out_apt": "羽田 (HND) ➔ 新千歳 (CTS)", "in_apt": "新千歳 (CTS) ➔ 羽田 (HND)", "out_times": ["06:50–08:25", "10:30–12:05", "16:00–17:35"], "base": 13800},
                {"name": "JAL", "out_apt": "羽田 (HND) ➔ 新千歳 (CTS)", "in_apt": "新千歳 (CTS) ➔ 羽田 (HND)", "out_times": ["07:30–09:05", "12:00–13:35", "17:30–19:05"], "base": 14200},
                {"name": "Peach", "out_apt": "成田 (NRT) ➔ 新千歳 (CTS)", "in_apt": "新千歳 (CTS) ➔ 成田 (NRT)", "out_times": ["08:00–09:40", "14:10–15:50"], "base": 6800},
                {"name": "Spring Japan", "out_apt": "成田 (NRT) ➔ 新千歳 (CTS)", "in_apt": "新千歳 (CTS) ➔ 成田 (NRT)", "out_times": ["09:15–11:00"], "base": 6200}
            ]
        }
    }

    key = f"{origin_code}-{dest_code}"
    if key not in route_configs:
        return None

    config = route_configs[key]
    outbound_flights = []
    inbound_flights = []

    date_hash = int(datetime.datetime.strptime(outbound_date, "%Y-%m-%d").timestamp()) % 1000

    for air in config["airlines"]:
        for idx, t in enumerate(air["out_times"]):
            variation = (date_hash * (idx + 1) * 37) % 1500 - 700
            final_price = max(3000, air["base"] + variation)

            outbound_flights.append({
                "flight_num": air["name"],
                "airport": air["out_apt"],
                "time": t,
                "price": final_price
            })

            inbound_price = max(3000, air["base"] + ((date_hash + 50) * (idx + 1) * 23) % 1500 - 700)
            inbound_flights.append({
                "flight_num": air["name"],
                "airport": air["in_apt"],
                "time": t,
                "price": inbound_price
            })

    min_out = min(f["price"] for f in outbound_flights)
    min_in = min(f["price"] for f in inbound_flights)

    return {
        "id": key,
        "route_name": config["name"],
        "airline": outbound_flights[0]["flight_num"],
        "outbound_date": outbound_date,
        "inbound_date": inbound_date,
        "outbound_flights": outbound_flights,
        "inbound_flights": inbound_flights,
        "total_min_price": min_out + min_in
    }

def main():
    today = datetime.date.today()
    schedules_data = []

    routes = [
        ("OSA", "OKA"),
        ("TYO", "OKA"),
        ("TYO", "FUK"),
        ("TYO", "CTS"),
    ]

    for day_offset in range(30, 33):
        outbound = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        inbound = (today + timedelta(days=day_offset + 3)).strftime("%Y-%m-%d")

        for orig, dest in routes:
            data = generate_route_flights(orig, dest, outbound, inbound)
            if data:
                schedules_data.append(data)

    jst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    updated_at_str = jst_now.strftime("%Y年%m月%d日 %H:%M JST")

    output_data = {
        "updated_at": updated_at_str,
        "schedules": schedules_data
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ データ更新完了: {updated_at_str}")

if __name__ == "__main__":
    main()
