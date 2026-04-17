import os
from dotenv import load_dotenv
from google.cloud import firestore

# .envファイルを読み込む
load_dotenv()

# プロジェクトIDを環境変数から取得
project_id = os.getenv("GCP_PROJECT_ID")

# Firestore クライアントの初期化（環境変数のIDを使う）
db = firestore.Client(project=project_id)

# データを書き込むテスト
doc_ref = db.collection("test_collection").document("test_doc")
doc_ref.set({
    "name": "Digital Passbook Test",
    "status": "success",
    "message": "Hello Firestore via .env!"
})

print("データを書き込みました！")

# --- 読み取りテストの追記 ---
print("Firestoreからデータを読み取ります...")
doc = doc_ref.get()
if doc.exists:
    data = doc.to_dict()
    print(f"成功！取得した内容: {data}")
else:
    print("エラー：データが見つかりませんでした。")
