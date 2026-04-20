import json
import requests

def fetch_current_balance(company_id, walletable_id):
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            tokens = json.load(f)
            access_token = tokens["access_token"]
    except:
        return

    # 一覧取得エンドポイントを使用
    url = f"https://api.freee.co.jp/api/1/walletables?company_id={company_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "FREEE-VERSION": "2020-06-15"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        walletables = response.json().get("walletables", [])
        # 指定した口座 ID を探す
        target = next((w for w in walletables if w["id"] == walletable_id), None)
        
        if target:
            print(f"\n--- 残高確認 ---")
            print(f"口座名: {target.get('name')}")
            # freee APIの残高フィールド名は 'walletable_balance' です
            balance = target.get('walletable_balance')
            if balance is not None:
                print(f"現在の登録残高: {balance:,} 円")
            else:
                print(f"残高フィールドが見つかりませんでした。取得可能なデータ: {list(target.keys())}")
        else:
            print(f"ID: {walletable_id} の口座が見つかりませんでした。")
    else:
        print(f"エラー: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    fetch_current_balance(12610654, 4717432)
