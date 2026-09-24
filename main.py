import os
import json
from datetime import datetime

# 条件設定
SEARCH_PARAMS = {
    "route": "OSA (大阪すべて) ⇆ OKA (沖縄/那覇)",
    "outbound_date": "2027-02-05",  # 行き
    "inbound_date": "2027-02-08",   # 帰り
    "airline": "ANA"
}

def generate_flight_data():
    """
    全便価格データを生成／取得する関数
    ※現在はダミーデータです。本物データ連携時もこの形式で書き出します。
    """
    outbound_flights = [
        {"flight_num": "ANA761", "time": "08:00 発 -> 10:15 着", "price": 16000},
        {"flight_num": "ANA763", "time": "11:15 発 -> 13:30 着", "price": 14500}, # 最安値
        {"flight_num": "ANA767", "time": "14:40 発 -> 16:55 着", "price": 18000},
        {"flight_num": "ANA769", "time": "17:30 発 -> 19:45 着", "price": 20000},
        {"flight_num": "ANA773", "time": "19:15 発 -> 21:30 着", "price": 22000}, # 最終便
    ]
    
    inbound_flights = [
        {"flight_num": "ANA762", "time": "08:00 発 -> 10:00 着", "price": 16000}, # 始発便
        {"flight_num": "ANA764", "time": "11:10 発 -> 13:05 着", "price": 15000}, # 最安値
        {"flight_num": "ANA768", "time": "14:20 発 -> 16:15 着", "price": 17500},
        {"flight_num": "ANA770", "time": "18:00 発 -> 19:55 着", "price": 19000},
        {"flight_num": "ANA772", "time": "20:30 発 -> 22:25 着", "price": 20000}, # 最終便
    ]

    min_outbound = min(f["price"] for f in outbound_flights)
    min_inbound = min(f["price"] for f in inbound_flights)
    total_min_price = min_outbound + min_inbound

    # Webページ（index.html）で読み込むデータオブジェクト
    data = {
        "route": SEARCH_PARAMS["route"],
        "outbound_date": SEARCH_PARAMS["outbound_date"],
        "inbound_date": SEARCH_PARAMS["inbound_date"],
        "total_min_price": total_min_price,
        "outbound_flights": outbound_flights,
        "inbound_flights": inbound_flights,
        "link": "https://www.ana.co.jp/",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return data

def main():
    data = generate_flight_data()
    
    # Webページ用に data.json として保存
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print("Web用データ (data.json) の更新に成功しました！")

if __name__ == "__main__":
    main()
