
import os
import requests

# GitHub SecretsからDiscordのWebhook URLを取得
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 目標設定（円）
TARGET_PRICE = 15000

SEARCH_PARAMS = {
    "origin": "TYO (東京)",
    "destination": "OKA (沖縄)",
    "date": "2026-11-01"
}

def fetch_flight_prices(params):
    """
    航空券価格を取得する関数
    ※ 実際の運用時はSkyscanner APIやAmadeus APIなどの処理に差し替えます。
    """
    print(f"価格確認中: {params['origin']} -> {params['destination']} ({params['date']})")
    
    # テスト用ダミーデータ
    return {
        "min_price": 12800,
        "airline": "Peach / Jetstar 比較",
        "link": "https://www.skyscanner.jp/"
    }

def send_discord_alert(data):
    """DiscordのWebhookを使って通知を送信"""
    payload = {
        "content": (
            f"🚨 **航空券の値下がりアラート！** 🚨\n\n"
            f"**【区間】**: {SEARCH_PARAMS['origin']} ➔ {SEARCH_PARAMS['destination']}\n"
            f"**【日付】**: {SEARCH_PARAMS['date']}\n"
            f"**【最安値】**: **{data['min_price']:,} 円**（目標: {TARGET_PRICE:,} 円）\n\n"
            f"▼ 予約・詳細はこちら\n{data['link']}"
        )
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print("Discordへの通知送信に成功しました！")
    else:
        print(f"送信失敗: {response.status_code} - {response.text}")

def main():
    flight_data = fetch_flight_prices(SEARCH_PARAMS)
    current_price = flight_data["min_price"]
    
    print(f"取得した最安値: {current_price}円")
    
    # 目標価格以下の時に通知
    if current_price <= TARGET_PRICE:
        send_discord_alert(flight_data)
    else:
        print("目標価格以上のため通知をスキップしました。")

if __name__ == "__main__":
    main()
