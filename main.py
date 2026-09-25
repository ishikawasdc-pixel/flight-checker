import json
import datetime
from datetime import timedelta
from fast_flights import FlightData, Passengers, Result, Trip, FlightSearch, FlightFilter, Airport, Currency

def get_real_flights(origin_code, dest_code, date_str):
    """
    fast-flightsライブラリを使用してGoogleフライトからリアルタイムの便データを取得する
    """
    flights = []
    try:
        filter_opts = FlightFilter(
            trip=Trip.ONE_WAY,
            passengers=Passengers(adults=1),
            currency=Currency.JPY
        )
        
        # FlightSearchオブジェクトの作成
        search = FlightSearch(
            flight_data=[
                FlightData(
                    date=date_str,
                    from_airport=Airport(origin_code),
                    to_airport=Airport(dest_code)
                )
            ],
            filter=filter_opts
        )

        result: Result = search.get()
        
        # 取得できた結果から上位便を抽出
        if result and result.current_price_result and result.current_price_result.flights:
            for f in result.current_price_result.flights[:5]:
                airline_name = f.airline if hasattr(f, 'airline') and f.airline else "主要航空会社"
                price_val = f.price if hasattr(f, 'price') and f.price else 0
                time_val = f.departure_time if hasattr(f, 'departure_time') and f.departure_time else "時間指定なし"
                
                if price_val > 0:
                    flights.append({
                        "flight_num": airline_name,
                        "time": time_val,
                        "price": price_val
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

        # 取得できた場合
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
