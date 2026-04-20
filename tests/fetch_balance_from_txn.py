import json
import requests

def get_latest_balance(company_id, walletable_id):
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            access_token = json.load(f)["access_token"]
    except:
        return

    # 最新の1件だけ取得
    url = f"https://api.freee.co.jp/api/1/wallet_txns?company_id={company_id}&walletable_type=bank_account&walletable_id={walletable_id}&limit=1"
    headers = {"Authorization": f"Bearer {access_token}", "FREEE-VERSION": "2020-06-15"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        txns = response.json().get("wallet_txns", [])
        if txns:
            latest = txns[0]
            balance = latest.get("balance")
            date = latest.get("date")
            print(f"\n--- 最新明細時点の残高 ---")
            print(f"日付: {date}")
            if balance is not None:
                print(f"残高: {balance:,} 円")
            else:
                print(f"データ構造: {list(latest.keys())}")
                print("この明細データに残高フィールド(balance)は含まれていませんでした。")
        else:
            print("明細が見つかりませんでした。")
    else:
        print(f"エラー: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    get_latest_balance(12610654, 4717432)
