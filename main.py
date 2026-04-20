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
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        self.company_id = os.getenv("FREEE_COMPANY_ID")
        self.company_name = os.getenv("FREEE_COMPANY_NAME")
        self.walletable_id = os.getenv("FREEE_WALLETABLE_ID")
        self.service_name = os.getenv("FREEE_SERVICE_NAME")

        self.db = firestore.Client(project=self.project_id)

    def _get_access_token(self):
        try:
            with open("tokens.json", "r", encoding="utf-8") as f:
                return json.load(f)["access_token"]
        except:
            print("エラー: tokens.json が読み込めません。")
            return None

    def fetch_freee_transactions(self, days=30):
        access_token = self._get_access_token()
        if not access_token: return []

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
        headers = {"Authorization": f"Bearer {access_token}", "FREEE-VERSION": "2022-04-01"}

        response = requests.get(url, headers=headers, params=params)
        return response.json().get("wallet_txns", []) if response.status_code == 200 else []

    def get_walletable_info(self):
        """口座の最新情報を取得"""
        access_token = self._get_access_token()
        if not access_token: return {}
        
        url = f"https://api.freee.co.jp/api/1/walletables?company_id={self.company_id}"
        headers = {"Authorization": f"Bearer {access_token}", "FREEE-VERSION": "2022-04-01"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                wallets = response.json().get("walletables", [])
                target_id = str(self.walletable_id).strip()
                return next((w for w in wallets if str(w["id"]) == target_id), {})
        except:
            pass
        return {}

    def send_discord_notification(self, count, balance, sync_date_detailed, app_time):
        """Discordに同期完了通知を送信"""
        if not self.webhook_url: return

        # 銀行同期日時の整形 (Tやタイムゾーン、秒を整理)
        # 詳細な時刻が取れている場合はそれを使用し、日付のみの場合は日付のみを表示
        if sync_date_detailed:
            formatted_bank_sync = sync_date_detailed.replace('T', ' ').split('+')[0].split('.')[0]
        else:
            formatted_bank_sync = "不明"

        header = "✅ **デジタル通帳 同期完了**"
        content = (
            f"{header}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🏢 **事業所**: {self.company_name}\n"
            f"🏦 **対象口座**: {self.service_name}\n"
            f"📥 **同期明細**: {count} 件\n"
            f"💰 **最新残高**: {balance:,} 円\n"
            f"🕒 **銀行同期**: {formatted_bank_sync}\n"
            f"🚀 **アプリ更新**: {app_time}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 [freee ログイン](<https://secure.freee.co.jp/>)\n"
            f"🛠️ [GitHub Repo](<https://github.com/zecu32/freee-gcp-digital-passbook>)"
        )
        
        payload = {"content": content}
        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f"通知送信エラー: {e}")

    def sync_to_firestore(self, transactions):
        if not transactions:
            return 0

        batch = self.db.batch()
        count = 0
        for txn in transactions:
            txn_id = str(txn["id"])
            doc_ref = self.db.collection("companies").document(str(self.company_id)) \
                             .collection("bank_accounts").document(str(self.walletable_id)) \
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
        batch.commit()
        return count

    def run(self):
        # アプリ実行時刻を記録
        app_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. 明細取得 & 同期
        txns = self.fetch_freee_transactions()
        count = self.sync_to_firestore(txns)
        
        # 2. 最新口座情報の取得
        wallet_info = self.get_walletable_info()
        
        # 残高の確定
        balance = wallet_info.get("walletable_balance")
        if balance is None:
            balance = txns[0].get("balance", 0) if txns else 0
            
        # 同期時刻の確定 (優先順位: 1.詳細日時 2.更新日 3.最新明細の日付)
        last_sync = wallet_info.get("last_synced_at")  # 詳細な日時
        if not last_sync:
            last_sync = wallet_info.get("update_date") # 日付のみ
        if not last_sync and txns:
            last_sync = txns[0].get("date")          # 明細の日付
            
        # 3. 通知送信
        self.send_discord_notification(count, balance, last_sync, app_time)
        print(f"同期成功: {count}件, 銀行同期日: {last_sync}, アプリ更新: {app_time}")

if __name__ == "__main__":
    sync_app = DigitalPassbookSync()
    sync_app.run()
