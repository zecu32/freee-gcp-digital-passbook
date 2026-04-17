import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数の確認
client_id = os.getenv("FREEE_CLIENT_ID")
client_secret = os.getenv("FREEE_CLIENT_SECRET")

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")