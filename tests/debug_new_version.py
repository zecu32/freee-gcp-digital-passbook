import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def debug_new_version():
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            access_token = json.load(f)["access_token"]
    except:
        return

    company_id = os.getenv("FREEE_COMPANY_ID")
    walletable_id = os.getenv("FREEE_WALLETABLE_ID")
    
    # バージョンを 2022-04-01 に変更
    url = f"https://api.freee.co.jp/api/1/walletables?company_id={company_id}"
    headers = {"Authorization": f"Bearer {access_token}", "FREEE-VERSION": "2022-04-01"}

    print(f"Testing with FREEE-VERSION: 2022-04-01")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        wallets = response.json().get("walletables", [])
        target = next((w for w in wallets if str(w["id"]) == str(walletable_id)), None)
        if target:
            print(json.dumps(target, indent=4, ensure_ascii=False))
        else:
            print("Target not found.")
    else:
        print(f"Error: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    debug_new_version()
