import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def debug_walletable_data():
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            access_token = json.load(f)["access_token"]
    except:
        return

    company_id = os.getenv("FREEE_COMPANY_ID")
    walletable_id = os.getenv("FREEE_WALLETABLE_ID")
    
    url = f"https://api.freee.co.jp/api/1/walletables?company_id={company_id}"
    headers = {"Authorization": f"Bearer {access_token}", "FREEE-VERSION": "2020-06-15"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        wallets = response.json().get("walletables", [])
        target = next((w for w in wallets if str(w["id"]) == str(walletable_id)), None)
        
        if target:
            print(f"\n--- 広島銀行の全フィールドデータ ---")
            print(json.dumps(target, indent=4, ensure_ascii=False))
        else:
            print("対象の口座が見つかりません。")
            print("取得した全ID:", [w["id"] for w in wallets])
    else:
        print(f"エラー: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    debug_walletable_data()
