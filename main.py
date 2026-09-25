import json
import datetime
from datetime import timedelta
import random

def generate_flight_data():
    """
    主要路線（東京、大阪、沖縄、福岡、札幌）に対応したデータ生成スクリプト
    """
    # 検索対象路線の拡充
    routes = [
        # 大阪発
        {"origin": "ITM", "origin_name": "大阪 (OSA)", "dest": "OKA", "dest_name": "沖縄 (OKA)"},
        {"origin": "ITM", "origin_name": "大阪 (OSA)", "dest": "FUK", "dest_name": "福岡 (FUK)"},
        {"origin": "ITM", "origin_name": "大阪 (OSA)", "dest": "TYO", "dest_name": "東京 (TYO)"},
        {"origin": "ITM", "origin_name": "大阪 (OSA)", "dest": "CTS", "dest_name": "札幌 (CTS)"},
        # 東京発
        {"origin": "TYO", "origin_name": "東京 (TYO)", "dest": "OKA", "dest_name": "沖縄 (OKA)"},
        {"origin": "TYO", "origin_name": "東京 (TYO)", "dest": "FUK", "dest_name": "福岡 (FUK)"},
        {"origin": "TYO", "origin_name": "東京 (TYO)", "dest": "CTS", "dest_name": "札幌 (CTS)"},
        {"origin": "TYO", "origin_name": "東京 (TYO)", "dest": "OSA", "dest_name": "大阪 (OSA)"},
    ]

    # 日付設定 (実行日の30日後〜33日後)
    today = datetime.date.today()
    outbound_date_str = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    inbound_date_str = (today + timedelta(days=33)).strftime("%Y-%m-%d")

    schedules_data = []

    print(f"--- データ自動生成開始 ({outbound_date_str} 〜 {inbound_date_str}) ---")

    for r in routes:
        route_display_name = f"{r['origin_name']} ➔ {r['dest_name']}"
        
        airlines_config = [
            {"code": "ANA", "outbound_num": "NH761", "inbound_num": "NH762", "base_price": 15000},
            {"code": "JAL", "outbound_num": "JL2081", "inbound_num": "JL2082", "base_price": 14500}
        ]

        for config in airlines_config:
            airline = config["code"]
            
            price_fluctuation = random.choice([-1000, -500, 0, 500, 1500])
            out_price_1 = config["base_price"] + price_fluctuation
            out_price_2 = config["base_price"] + price_fluctuation + 1500

            in_price_1 = config["base_price"] + price_fluctuation - 300
            in_price_2 = config["base_price"] + price_fluctuation + 800

            outbound_flights = [
                {"flight_num": f"{config['outbound_num']}", "time": "08:30 - 10:45", "price": out_price_1},
                {"flight_num": f"{config['outbound_num'][:-1]}3", "time": "14:15 - 16:30", "price": out_price_2}
            ]

            inbound_flights = [
                {"flight_num": f"{config['inbound_num']}", "time": "11:30 - 13:30", "price": in_price_1},
                {"flight_num": f"{config['inbound_num'][:-1]}4", "time": "17:30 - 19:30", "price": in_price_2}
            ]

            min_outbound = min(f["price"] for f in outbound_flights)
            min_inbound = min(f["price"] for f in inbound_flights)

            schedules_data.append({
                "id": f"{r['origin']}-{r['dest']}-{airline}",
                "route_name": route_display_name,
                "airline": airline,
                "outbound_date": outbound_date_str,
                "inbound_date": inbound_date_str,
                "outbound_flights": outbound_flights,
                "inbound_flights": inbound_flights,
                "total_min_price": min_outbound + min_inbound
            })

    # 現在日時（JST）
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    jst_now = now_utc + datetime.timedelta(hours=9)
    updated_at_str = jst_now.strftime("%Y年%m月%d日 %H:%M JST")

    output_data = {
        "updated_at": updated_at_str,
        "schedules": schedules_data
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 全路線のデータ更新が完了しました！(最終更新: {updated_at_str})")

if __name__ == "__main__":
    generate_flight_data()
