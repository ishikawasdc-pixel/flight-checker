import json
import datetime
from datetime import timedelta
import time
import re
from playwright.sync_api import sync_playwright

def fetch_google_flights_data(page, origin, dest, date_str):
    """
    Googleフライトから便情報を確実に取得する関数
    """
    # 日本語・日本地域指定でGoogle FlightsのURLを生成
    url = f"https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{origin}%20on%20{date_str}%20one-way&hl=ja&gl=jp&curr=JPY"
    print(f"URLアクセス中: {url}")
    
    flights = []
    try:
        # ページへアクセス
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(4) # 動的コンテンツの描画待機

        # 同意ボタンやポップアップがあれば閉じる処理
        try:
            consent_btn = page.query_selector('button[aria-label*="同意"], button[aria-label*="Accept"]')
            if consent_btn:
                consent_btn.click()
                time.sleep(2)
        except Exception:
            pass

        # 画面を少しスクロールして隠れている要素を読み込ませる
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(2)

        # 便のリストカード要素を取得
        cards = page.query_selector_all('li.pI213d, div.R6A13b, li.K12pMc')
        print(f"  -> 発見した要素数: {len(cards)}")

        for card in cards:
            try:
                text = card.inner_text()
                if not text or "￥" not in text:
                    continue

                # 価格（￥XX,XXX）を抽出
                price_match = re.search(r'￥([0-9,]+)', text)
                if not price_match:
                    continue
                price = int(price_match.group(1).replace(',', ''))

                # 時間帯（例: 08:00～10:15 / 08:00 - 10:15 / 08:00–10:15）を抽出
                time_match = re.search(r'(\d{1,2}:\d{2})\s*[–\-～〜]\s*(\d{1,2}:\d{2})', text)
                flight_time = time_match.group(0) if time_match else "時間情報"

                # 航空会社の判定
                airline = "その他の航空会社"
                if "ANA" in text or "全日空" in text:
                    airline = "ANA"
                elif "JAL" in text or "日本航空" in text:
                    airline = "JAL"
                elif "Peach" in text or "ピーチ" in text:
                    airline = "Peach"
                elif "Jetstar" in text or "ジェットスター" in text:
                    airline = "Jetstar"
                elif "スカイマーク" in text or "Skymark" in text:
                    airline = "Skymark"
                elif "ソラシド" in text or "Solaseed" in text:
                    airline = "Solaseed Air"
                elif "スターフライヤー" in text or "StarFlyer" in text:
                    airline = "StarFlyer"

                flights.append({
                    "flight_num": airline,
                    "time": flight_time,
                    "price": price
                })
            except Exception:
                continue

    except Exception as e:
        print(f"  -> エラー発生 ({origin} -> {dest}): {e}")

    return flights

def main():
    today = datetime.date.today()
    outbound_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    inbound_date = (today + timedelta(days=33)).strftime("%Y-%m-%d")

    # 大阪全域（OSA）、東京全域（TYO）のマルチ空港コードに対応
    route_targets = [
        {"origin_code": "OSA", "origin_label": "大阪 (OSA)", "dest_code": "OKA", "dest_label": "沖縄 (OKA)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "OKA", "dest_label": "沖縄 (OKA)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "FUK", "dest_label": "福岡 (FUK)"},
        {"origin_code": "TYO", "origin_label": "東京 (TYO)", "dest_code": "CTS", "dest_label": "札幌 (CTS)"},
    ]

    schedules_data = []

    with sync_playwright() as p:
        # Chromiumをステルスモードで起動（Bot判定対策）
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--window-size=1280,800'
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
            viewport={'width': 1280, 'height': 800}
        )
        
        page = context.new_page()

        for route in route_targets:
            route_name = f"{route['origin_label']} ➔ {route['dest_label']}"
            print(f"--- 検索開始: {route_name} ---")

            outbound_flights = fetch_google_flights_data(page, route["origin_code"], route["dest_code"], outbound_date)
            time.sleep(3)

            inbound_flights = fetch_google_flights_data(page, route["dest_code"], route["origin_code"], inbound_date)
            time.sleep(3)

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

    jst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    updated_at_str = jst_now.strftime("%Y年%m月%d日 %H:%M JST")

    output_data = {
        "updated_at": updated_at_str,
        "schedules": schedules_data
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 実データ更新完了: {updated_at_str} (取得路線数: {len(schedules_data)})")

if __name__ == "__main__":
    main()
