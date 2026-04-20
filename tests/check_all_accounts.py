import json
import requests

def check_all():
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            tokens = json.load(f)
            access_token = tokens["access_token"]
    except:
        print("tokens.json が読み込めません。")
        return

    # 1. 事業所一覧を再取得
    comp_url = "https://api.freee.co.jp/api/1/companies"
    headers = {"Authorization": f"Bearer {access_token}", "FREEE-VERSION": "2020-06-15"}
    
    response = requests.get(comp_url, headers=headers)
    if response.status_code != 200:
        print(f"事業所取得エラー: {response.status_code}")
        return
        
    companies = response.json().get("companies", [])

    for comp in companies:
        print(f"\n===== 事業所: {comp['display_name']} (ID: {comp['id']}) =====")
        # 2. その事業所の口座一覧を取得
        wallet_url = f"https://api.freee.co.jp/api/1/walletables?company_id={comp['id']}"
        wallets_response = requests.get(wallet_url, headers=headers)
        
        if wallets_response.status_code == 200:
            wallets = wallets_response.json().get("walletables", [])
            if not wallets:
                print("  (口座が見つかりません)")
            for w in wallets:
                print(f"  - [{w['type']}] {w['name']} (ID: {w['id']})")
        else:
            print(f"  口座取得エラー: {wallets_response.status_code}")

if __name__ == "__main__":
    check_all()
