import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def debug_detail():
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            access_token = json.load(f)["access_token"]
    except:
        return

    company_id = os.getenv("FREEE_COMPANY_ID")
    walletable_id = os.getenv("FREEE_WALLETABLE_ID")
    
    # 個別取得エンドポイント
    url = f"https://api.freee.co.jp/api/1/walletables/{walletable_id}?company_id={company_id}"
    headers = {"Authorization": f"Bearer {access_token}", "FREEE-VERSION": "2020-06-15"}

    response = requests.get(url, headers=headers)
    print(f"ステータス: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    else:
        print(response.text)

if __name__ == "__main__":
    debug_detail()
