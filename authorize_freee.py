import os
from urllib.parse import urlencode
from dotenv import load_dotenv

def generate_auth_url():
    load_dotenv()
    
    client_id = os.getenv("FREEE_CLIENT_ID")
    redirect_uri = os.getenv("FREEE_REDIRECT_URI")
    
    if not client_id or not redirect_uri:
        print("エラー: .env ファイルに FREEE_CLIENT_ID または FREEE_REDIRECT_URI が設定されていません。")
        return

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
    }
    
    auth_base_url = "https://accounts.secure.freee.co.jp/public_api/authorize"
    url = f"{auth_base_url}?{urlencode(params)}"
    
    print("\n--- freee API 認可テスト ---")
    print("1. 以下のURLをブラウザで開いて、アプリを承認してください:")
    print(f"\n{url}\n")
    print("2. 承認後、ブラウザのアドレスバーに表示される URL から 'code=' 以降の文字列をコピーしてください。")
    print("   例: http://localhost:8000/callback?code=XXXXXX  ← この XXXXXX の部分")

if __name__ == "__main__":
    generate_auth_url()
