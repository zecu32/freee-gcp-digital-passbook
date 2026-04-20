import json
import requests
from datetime import datetime, timedelta

def fetch_transactions(company_id, walletable_id):
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            tokens = json.load(f)
            access_token = tokens["access_token"]
    except:
        print("tokens.json が見つかりません。")
        return

    # 直近30日間の明細を取得してみる
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    url = f"https://api.freee.co.jp/api/1/wallet_txns?company_id={company_id}&walletable_type=bank_account&walletable_id={walletable_id}&start_date={start_date}&end_date={end_date}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "FREEE-VERSION": "2020-06-15"
    }

    print(f"広島銀行 (ID: {walletable_id}) の明細を {start_date} から取得中...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        txns = data.get("wallet_txns", [])
        print(f"\n--- 取得結果: {len(txns)} 件の明細が見つかりました ---")
        for t in txns[:10]: # 最初の10件を表示
            date = t.get('date')
            amount = t.get('amount')
            desc = t.get('description')
            print(f"日付: {date}, 金額: {amount}, 内容: {desc}")
    else:
        print(f"エラー: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    KOMA_ID = 12610654
    HIROSHIMA_BANK_ID = 4717432
    fetch_transactions(KOMA_ID, HIROSHIMA_BANK_ID)
