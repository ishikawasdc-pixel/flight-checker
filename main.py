import os
import requests

# GitHub SecretsからDiscordのWebhook URLを取得
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 目標設定（往復の合計上限金額）
TARGET_PRICE = 35000

SEARCH_PARAMS = {
    "origin": "OSA (大阪すべて)",
    "destination": "OKA (沖縄/那覇)",
    "outbound_date": "2027-02-05",  # 往路（行き）
    "inbound_date": "2027-02-08",   # 復路（帰り）
    "airline": "ANA"
}

def fetch_flight_prices(params):
    """
    航空券価格を取得する関数
    ※ 実際の運用時はSkyscanner APIやAmadeus API等のレスポンスを加工します。
    """
    print(f"価格確認中: {params['origin']} <-> {params['destination']}")
    
    # テスト用ダミーデータ（始発〜最終便の価格幅と、往復最安値）
    return {
        "outbound_first_flight": 15000,  # 往路・始発便
        "outbound_last_flight": 22000,   # 往路・最終便
        "outbound_min": 14500,           # 往路・最安値
        "inbound_first_flight": 16000,   # 復路・始発便
        "inbound_last_flight": 20000,    # 復路・最終便
        "inbound_min": 15000,            # 復路・最安値
        "total_round_trip": 29500,       # 往復合計最安値
        "link": "https://www.ana.co.jp/"
    }

def send_discord_alert(data):
    """DiscordのWebhookを使って通知を送信"""
    payload = {
        "content": (
            f"🚨 **【往復】航空券の価格アラート！** 🚨\n\n"
            f"**【区間】**: {SEARCH_PARAMS['origin']} ⇆ {SEARCH_PARAMS['destination']} ({SEARCH_PARAMS['airline']})\n"
            f"**【日程】**: 行き {SEARCH_PARAMS['outbound_date']} ／ 帰り {SEARCH_PARAMS['inbound_date']}\n\n"
            f"✈️ **【行き（往路）価格帯】**\n"
            f"・最安値: **{data['outbound_min']:,} 円**\n"
            f"・始発便: {data['outbound_first_flight']:,} 円 ／ 最終便: {data['outbound_last_flight']:,} 円\n\n"
            f"✈️ **【帰り（復路）価格帯】**\n"
            f"・最安値: **{data['inbound_min']:,} 円**\n"
            f"・始発便: {data['inbound_first_flight']:,} 円 ／ 最終便: {data['inbound_last_flight']:,} 円\n\n"
            f"💰 **【往復合計最安値】**: **{data['total_round_trip']:,} 円**（目標: {TARGET_PRICE:,} 円以下）\n\n"
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
    total_price = flight_data["total_round_trip"]
    
    print(f"取得した往復最安値: {total_price}円")
    
    # 往復合計が目標価格以下の時に通知
    if total_price <= TARGET_PRICE:
        send_discord_alert(flight_data)
    else:
        print("目標価格以上のため通知をスキップしました。")

if __name__ == "__main__":
    main()
import os
import requests

# GitHub SecretsからDiscordのWebhook URLを取得
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 目標設定（例：20,000円以下なら通知）
TARGET_PRICE = 20000

SEARCH_PARAMS = {
    "origin": "OSA (大阪すべて / 伊丹・関空・神戸)",
    "destination": "OKA (沖縄/那覇)",
    "date": "2027-02-05",  # ※出発日に合わせて変更してください
    "airline": "ANA"
}

def fetch_flight_prices(params):
    print(f"価格確認中: {params['origin']} -> {params['destination']} ({params['date']})")
    
    # テスト用ダミーデータ（ANA 大阪→沖縄想定）
    return {
        "min_price": 14500,
        "airline": "ANA",
        "link": "https://www.ana.co.jp/"
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
