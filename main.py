import json
import datetime
from datetime import timedelta

def generate_route_flights(origin_code, dest_code, outbound_date, inbound_date):
    """
    主要路線データとGoogleフライト直接検索リンクを生成
    """
    route_configs = {
        "OSA-OKA": {
            "name": "大阪 (OSA) ➔ 沖縄 (OKA)",
            "origin_label": "大阪 (OSA)",
            "dest_label": "沖縄 (OKA)",
            "airlines": [
                {"name": "Peach", "out_apt": "関西 (KIX) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 関西 (KIX)", "base": 8200},
                {"name": "JAL", "out_apt": "伊丹 (ITM) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 伊丹 (ITM)", "base": 15800},
                {"name": "ANA", "out_apt": "伊丹 (ITM) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 伊丹 (ITM)", "base": 16200},
                {"name": "Jetstar", "out_apt": "関西 (KIX) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 関西 (KIX)", "base": 7800}
            ]
        },
        "TYO-OKA": {
            "name": "東京 (TYO) ➔ 沖縄 (OKA)",
            "origin_label": "東京 (TYO)",
            "dest_label": "沖縄 (OKA)",
            "airlines": [
                {"name": "ANA", "out_apt": "羽田 (HND) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 羽田 (HND)", "base": 17800},
                {"name": "JAL", "out_apt": "羽田 (HND) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 羽田 (HND)", "base": 18200},
                {"name": "Peach", "out_apt": "成田 (NRT) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 成田 (NRT)", "base": 9800},
                {"name": "Skymark", "out_apt": "羽田 (HND) ➔ 那覇 (OKA)", "in_apt": "那覇 (OKA) ➔ 羽田 (HND)", "base": 12500}
            ]
        },
        "TYO-FUK": {
            "name": "東京 (TYO) ➔ 福岡 (FUK)",
            "origin_label": "東京 (TYO)",
            "dest_label": "福岡 (FUK)",
            "airlines": [
                {"name": "ANA", "out_apt": "羽田 (HND) ➔ 福岡 (FUK)", "in_apt": "福岡 (FUK) ➔ 羽田 (HND)", "base": 14500},
                {"name": "JAL", "out_apt": "羽田 (HND) ➔ 福岡 (FUK)", "in_apt": "福岡 (FUK) ➔ 羽田 (HND)", "base": 14800},
                {"name": "StarFlyer", "out_apt": "羽田 (HND) ➔ 福岡 (FUK)", "in_apt": "福岡 (FUK) ➔ 羽田 (HND)", "base": 12800}
            ]
        },
        "TYO-CTS": {
            "name": "東京 (TYO) ➔ 札幌 (CTS)",
            "origin_label": "東京 (TYO)",
            "dest_label": "札幌 (CTS)",
            "airlines": [
                {"name": "ANA", "out_apt": "羽田 (HND) ➔ 新千歳 (CTS)", "in_apt": "新千歳 (CTS) ➔ 羽田 (HND)", "base": 13800},
                {"name": "JAL", "out_apt": "羽田 (HND) ➔ 新千歳 (CTS)", "in_apt": "新千歳 (CTS) ➔ 羽田 (HND)", "base": 14200},
                {"name": "Peach", "out_apt": "成田 (NRT) ➔ 新千歳 (CTS)", "in_apt": "新千歳 (CTS) ➔ 成田 (NRT)", "base": 6800},
                {"name": "Spring Japan", "out_apt": "成田 (NRT) ➔ 新千歳 (CTS)", "in_apt": "新千歳 (CTS) ➔ 成田 (NRT)", "base": 6200}
            ]
        }
    }

    key = f"{origin_code}-{dest_code}"
    if key not in route_configs:
        return None

    config = route_configs[key]
    outbound_flights = []
    inbound_flights = []

    # Googleフライトの直接検索URL作成
    google_flight_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest_code}%20from%20{origin_code}%20on%20{outbound_date}%20through%20{inbound_date}"

    for air in config["airlines"]:
        outbound_flights.append({
            "flight_num": air["name"],
            "airport": air["out_apt"],
            "time": "目安相場表示",
            "price": air["base"],
            "url": google_flight_url
        })

        inbound_flights.append({
            "flight_num": air["name"],
            "airport": air["in_apt"],
            "time": "目安相場表示",
            "price": air["base"],
            "url": google_flight_url
        })

    min_out = min(f["price"] for f in outbound_flights)
    min_in = min(f["price"] for f in inbound_flights)

    return {
        "id": key,
        "route_name": config["name"],
        "airline": outbound_flights[0]["flight_num"],
        "outbound_date": outbound_date,
        "inbound_date": inbound_date,
        "google_flight_url": google_flight_url,
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
