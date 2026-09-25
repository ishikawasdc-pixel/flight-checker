import json
import datetime
from datetime import timedelta
import time
import re
from playwright.sync_api import sync_playwright

def fetch_google_flights_data(page, origin, dest, date_str):
    """
    Googleフライトにアクセスし、実際の最新価格情報を抽出する
    """
    # 検索用URL (一方向検索)
    url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{origin}%20on%20{date_str}%20one-way&hl=ja"
    print(f"URLアクセス中: {url}")
    
    try:
        # ページ遷移と十分な読み込み待機
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5) # 動的コンテンツのレンダリング待機
        
        flights = []
        
        # フライトリスト要素の取得（複数のセレクタで柔軟に対応）
        items = page.query_selector_all('li.pI213d, div[role="listitem"]')
        
        for item in items[:4]: # 上位4便を取得
            try:
                text_content = item.inner_text()
                
                # 金額（￥XX,XXX）を正規表現で抽出
                price_match = re.search(r'￥([0-9,]+)', text_content)
                if not price_match:
                    continue
                
                price = int(price_match.group(1).replace(',', ''))
                
                # 航空会社の判定（主要航空会社のキーワードマッチ）
                airline = "その他の航空会社"
                if "ANA" in text_content or "全日空" in text_content:
                    airline = "ANA"
                elif "JAL" in text_content or "日本航空" in text_content:
                    airline = "JAL"
                elif "ピーチ" in text_content or "Peach" in text_content:
                    airline = "Peach"
                elif "ジェットスター" in text_content or "Jetstar" in text_content:
                    airline = "Jetstar"
                elif "ソラシド" in text_content:
                    airline = "Solaseed Air"
                elif "スターフライヤー" in text_content:
                    airline = "StarFlyer"
                elif "スカイマーク" in text_content:
                    airline = "Skymark"

                # 時間（例: 08:00～10:15 や 08:00 - 10:15）の抽出
                time_match = re.search(r'(\d{1,2}:\d{2})\s*[–\-～]\s*(\d{1,2}:\d{2})', text_content)
                flight_time = time_match.group(0) if time_match else "時間情報取得中"

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
    # 30日後と33日後をターゲットに指定
    outbound_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    inbound_date = (today + timedelta(days=33)).strftime("%Y-%m-%d")

    route_targets = [
        {"origin_code": "ITM", "origin_label": "大阪 (OSA)", "dest_code": "OKA", "dest_label": "沖縄 (OKA)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "OKA", "dest_label": "沖縄 (OKA)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "FUK", "dest_label": "福岡 (FUK)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "CTS", "dest_label": "札幌 (CTS)"},
    ]

    schedules_data = []

    with sync_playwright() as p:
        # ボット判定を回避するためのオプションを追加
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ja-JP",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        for route in route_targets:
            route_name = f"{route['origin_label']} ➔ {route['dest_label']}"
            print(f"--- 実データ取得開始: {route_name} ---")

            outbound_flights = fetch_google_flights_data(page, route["origin_code"], route["dest_code"], outbound_date)
            time.sleep(2) # 連続アクセスによるブロック防止
            
            inbound_flights = fetch_google_flights_data(page, route["dest_code"], route["origin_code"], inbound_date)
            time.sleep(2)

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

    # JST時刻で更新日時を記録
    jst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    updated_at_str = jst_now.strftime("%Y年%m月%d日 %H:%M JST")

    output_data = {
        "updated_at": updated_at_str,
        "schedules": schedules_data
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 実データ更新完了: {updated_at_str}")

if __name__ == "__main__":
    main()
