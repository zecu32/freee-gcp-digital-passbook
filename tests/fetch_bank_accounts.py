import json
import requests

def fetch_walletables(company_id):
    # 保存されたトークンを読み込む
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            tokens = json.load(f)
            access_token = tokens["access_token"]
    except FileNotFoundError:
        print("エラー: tokens.json が見つかりません。先に認可を行ってください。")
        return

    url = f"https://api.freee.co.jp/api/1/walletables?company_id={company_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "FREEE-VERSION": "2020-06-15"
    }

    print(f"事業所 ID: {company_id} の口座一覧を取得中...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"\n--- 事業所 ID: {company_id} の口座一覧 ---")
        for item in data.get("walletables", []):
            print(f"口座ID: {item.get('id')}")
            print(f"  名前: {item.get('name')}")
            print(f"  種類: {item.get('type')}")
            # balance（残高）などの情報も取得可能です
            print(f"  登録残高: {item.get('walletable_balance', '不明')}")
            print("-" * 30)
    else:
        print(f"エラー: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    DEV_TEST_COMPANY_ID = 12611777
    fetch_walletables(DEV_TEST_COMPANY_ID)
