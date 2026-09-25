import json
import datetime
from datetime import timedelta
import time
from playwright.sync_api import sync_playwright

def fetch_google_flights_data(page, origin, dest, date_str):
    """
    GoogleフライトのURLを構築してアクセスし、実際の便情報と価格を取得する
    """
    # Google FlightsのダイレクトURL作成 (例: OSA -> OKA)
    url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{origin}%20on%20{date_str}%20one-way"
    print(f"URLアクセス中: {url}")
    
    try:
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(3) # ページの読み込み完了を少し待機
        
        flights = []
        # Googleフライトの便結果要素を取得
        cards = page.query_selector_all('li.pI213d')
        
        for card in cards[:3]: # 上位3便を取得
            try:
                # 航空会社名
                airline_elem = card.query_selector('div.sA23be')
                airline = airline_elem.inner_text().strip() if airline_elem else "不明"
                
                # 時間情報
                time_elem = card.query_selector('div.gB1p2c')
                flight_time = time_elem.inner_text().replace('\n', ' ').strip() if time_elem else "時間情報なし"
                
                # 価格情報
                price_elem = card.query_selector('div.YMlA3d span')
                price_str = price_elem.inner_text().replace('￥', '').replace(',', '').strip() if price_elem else "0"
                price = int(price_str) if price_str.isdigit() else 0

                if price > 0:
                    flights.append({
                        "flight_num": airline,
                        "time": flight_time,
                        "price": price
                    })
            except Exception as e:
                continue
                
        return flights
    except Exception as e:
        print(f"エラー発生 ({origin} -> {dest}): {e}")
        return []

def main():
    today = datetime.date.today()
    outbound_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    inbound_date = (today + timedelta(days=33)).strftime("%Y-%m-%d")

    # 検索対象の主要ルートリスト
    route_targets = [
        {"origin_code": "ITM", "origin_label": "大阪 (OSA)", "dest_code": "OKA", "dest_label": "沖縄 (OKA)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "OKA", "dest_label": "沖縄 (OKA)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "FUK", "dest_label": "福岡 (FUK)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "CTS", "dest_label": "札幌 (CTS)"},
    ]

    schedules_data = []

    with sync_playwright() as p:
        # ヘッドレスブラウザを起動
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            locale="ja-JP"
        )
        page = context.new_page()

        for route in route_targets:
            route_name = f"{route['origin_label']} ➔ {route['dest_label']}"
            print(f"--- 取得中: {route_name} ---")

            # 往路データ取得
            outbound_flights = fetch_google_flights_data(page, route["origin_code"], route["dest_code"], outbound_date)
            # 復路データ取得
            inbound_flights = fetch_google_flights_data(page, route["dest_code"], route["origin_code"], inbound_date)

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

        browser.close()

    # JST時刻の記録
    jst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    updated_at_str = jst_now.strftime("%Y年%m月%d日 %H:%M JST")

    output_data = {
        "updated_at": updated_at_str,
        "schedules": schedules_data
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 実データの更新完了: {updated_at_str}")

if __name__ == "__main__":
    main()
