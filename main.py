import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.cloud import firestore

# .envファイルを読み込む
load_dotenv()

class DigitalPassbookSync:
    def __init__(self):
        # 環境変数から設定を読込
        self.client_id = os.getenv("FREEE_CLIENT_ID")
        self.client_secret = os.getenv("FREEE_CLIENT_SECRET")
        self.project_id = os.getenv("GCP_PROJECT_ID")
        
        # 同期対象の設定
        self.company_id = os.getenv("FREEE_COMPANY_ID")
        self.company_name = os.getenv("FREEE_COMPANY_NAME")
        self.walletable_id = os.getenv("FREEE_WALLETABLE_ID")
        self.service_name = os.getenv("FREEE_SERVICE_NAME")

        self.db = firestore.Client(project=self.project_id)

    def _get_access_token(self):
        """tokens.jsonからアクセストークンを取得する"""
        try:
            with open("tokens.json", "r", encoding="utf-8") as f:
                return json.load(f)["access_token"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("エラー: 有効な tokens.json が見つかりません。")
            return None

    def fetch_freee_transactions(self, days=60):
        """freee APIから入出金明細を取得する"""
        access_token = self._get_access_token()
        if not access_token:
            return []

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        url = "https://api.freee.co.jp/api/1/wallet_txns"
        params = {
            "company_id": self.company_id,
            "walletable_type": "bank_account",
            "walletable_id": self.walletable_id,
            "start_date": start_date,
            "end_date": end_date
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "FREEE-VERSION": "2020-06-15"
        }

        print(f"freeeから {self.service_name} の明細を取得中... ({start_date} ~ {end_date})")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json().get("wallet_txns", [])
        else:
            print(f"APIエラー: {response.status_code}\n{response.text}")
            return []

    def sync_to_firestore(self, transactions):
        """取得した明細をFirestoreに同期する"""
        if not transactions:
            print("同期する明細がありません。")
            return

        print(f"{len(transactions)} 件の明細をFirestoreに同期します...")
        batch = self.db.batch()
        count = 0
        
        for txn in transactions:
            txn_id = str(txn["id"])
            doc_ref = self.db.collection("companies").document(self.company_id) \
                             .collection("bank_accounts").document(self.walletable_id) \
                             .collection("transactions").document(txn_id)
            
            data = {
                "date": txn["date"],
                "amount": txn["amount"],
                "balance": txn.get("balance", 0),
                "description": txn["description"],
                "entry_side": txn.get("entry_side"),
                "service_name": self.service_name,
                "company_name": self.company_name,
                "walletable_id": int(self.walletable_id),
                "company_id": int(self.company_id),
                "updated_at": firestore.SERVER_TIMESTAMP
            }
            
            batch.set(doc_ref, data, merge=True)
            count += 1
            
            if count % 500 == 0:
                batch.commit()
                batch = self.db.batch()

        if count > 0:
            batch.commit()
        
        print(f"同期完了！ {count} 件のドキュメントを更新しました。")

    def run(self):
        """一連の同期フローを実行"""
        txns = self.fetch_freee_transactions()
        self.sync_to_firestore(txns)

if __name__ == "__main__":
    sync_app = DigitalPassbookSync()
    sync_app.run()
