import json
import datetime
from datetime import timedelta
from fast_flights import FlightQuery, create_query, get_flights

def get_real_flights(origin_code, dest_code, date_str):
    """
    fast-flightsライブラリを使用してGoogleフライトから航空券データを取得
    """
    flights = []
    try:
        # クエリの作成
        query = create_query(
            flights=[
                FlightQuery(
                    date=date_str,
                    from_airport=origin_code,
                    to_airport=dest_code
                )
            ],
            trip="one-way",
            currency="JPY"
        )

        # フライト情報の取得
        result = get_flights(query)

        # 取得結果の解析
        if result and hasattr(result, 'flights') and result.flights:
            for f in result.flights[:5]:
                airline_name = getattr(f, 'airline', '主要航空会社') or '主要航空会社'
                price_val = getattr(f, 'price', 0) or 0
                time_val = getattr(f, 'departure_time', '時間指定なし') or '時間指定なし'

                if price_val > 0:
                    flights.append({
                        "flight_num": airline_name,
                        "time": str(time_val),
                        "price": int(price_val)
                    })

    except Exception as e:
        print(f"取得エラー ({origin_code} -> {dest_code}): {e}")

    return flights

def main():
    today = datetime.date.today()
    outbound_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    inbound_date = (today + timedelta(days=33)).strftime("%Y-%m-%d")

    route_targets = [
        {"origin_code": "OSA", "origin_label": "大阪 (OSA)", "dest_code": "OKA", "dest_label": "沖縄 (OKA)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "OKA", "dest_label": "沖縄 (OKA)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "FUK", "dest_label": "福岡 (FUK)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "CTS", "dest_label": "札幌 (CTS)"},
    ]

    schedules_data = []

    for route in route_targets:
        route_name = f"{route['origin_label']} ➔ {route['dest_label']}"
        print(f"--- 取得中: {route_name} ---")

        outbound_flights = get_real_flights(route["origin_code"], route["dest_code"], outbound_date)
        inbound_flights = get_real_flights(route["dest_code"], route["origin_code"], inbound_date)

        if outbound_flights:
            min_out = min(f["price"] for f in outbound_flights)
            min_in = min(f["price"] for f in inbound_flights) if inbound_flights else 0

            schedules_data.append({
                "id": f"{route['origin_code']}-{route['dest_code']}",
                "route_name": route_name,
                "airline": outbound_flights[0]["flight_num"],
                "outbound_date": outbound_date,
                "inbound_date": inbound_date,
                "outbound_flights": outbound_flights,
                "inbound_flights": inbound_flights if inbound_flights else outbound_flights,
                "total_min_price": min_out + min_in
            })

    jst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    updated_at_str = jst_now.strftime("%Y年%m月%d日 %H:%M JST")

    output_data = {
        "updated_at": updated_at_str,
        "schedules": schedules_data
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ データ更新完了: {updated_at_str} (取得件数: {len(schedules_data)})")

if __name__ == "__main__":
    main()
