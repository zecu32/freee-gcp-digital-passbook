import os
import requests
import json
from dotenv import load_dotenv

def get_access_token(auth_code):
    load_dotenv()
    
    client_id = os.getenv("FREEE_CLIENT_ID")
    client_secret = os.getenv("FREEE_CLIENT_SECRET")
    redirect_uri = os.getenv("FREEE_REDIRECT_URI")
    
    url = "https://accounts.secure.freee.co.jp/public_api/token"
    
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": redirect_uri
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print("アクセストークンを取得中...")
    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        tokens = response.json()
        with open("tokens.json", "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=4)
        print("成功！トークンを tokens.json に保存しました。")
        return tokens
    else:
        print(f"エラー: {response.status_code}")
        print(response.text)
        return None

def fetch_companies(access_token):
    url = "https://api.freee.co.jp/api/1/companies"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "FREEE-VERSION": "2020-06-15"
    }
    
    print("事業所一覧を取得中...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        companies = response.json()
        print("\n--- 取得した事業所一覧 ---")
        for comp in companies.get("companies", []):
            print(f"ID: {comp['id']}, 名前: {comp['display_name']}")
    else:
        print(f"事業所取得エラー: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        code = sys.argv[1]
        tokens = get_access_token(code)
        if tokens:
            fetch_companies(tokens["access_token"])
    else:
        print("認可コードを引数として渡してください。")
