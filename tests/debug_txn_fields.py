import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def debug_txn_fields():
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            access_token = json.load(f)["access_token"]
    except:
        return

    company_id = os.getenv("FREEE_COMPANY_ID")
    walletable_id = os.getenv("FREEE_WALLETABLE_ID")
    
    url = f"https://api.freee.co.jp/api/1/wallet_txns?company_id={company_id}&walletable_type=bank_account&walletable_id={walletable_id}&limit=1"
    headers = {"Authorization": f"Bearer {access_token}", "FREEE-VERSION": "2020-06-15"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        txns = response.json().get("wallet_txns", [])
        if txns:
            print(f"\n--- 明細の全フィールドデータ ---")
            print(json.dumps(txns[0], indent=4, ensure_ascii=False))
        else:
            print("明細がありません。")
    else:
        print(f"エラー: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    debug_txn_fields()
