import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.cloud import firestore
import gspread
import google.auth

# .envファイルを読み込む (ローカル実行用)
load_dotenv()

class DigitalPassbookSync:
    def __init__(self):
        # 環境変数から設定を読込
        self.client_id = os.getenv("FREEE_CLIENT_ID")
        self.client_secret = os.getenv("FREEE_CLIENT_SECRET")
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        
        self.company_id = os.getenv("FREEE_COMPANY_ID")
        self.company_name = os.getenv("FREEE_COMPANY_NAME")
        self.walletable_id = os.getenv("FREEE_WALLETABLE_ID")
        self.service_name = os.getenv("FREEE_SERVICE_NAME")

        self.db = firestore.Client(project=self.project_id)
        self.tokens_doc_ref = self.db.collection("settings").document("freee_tokens")

    def _get_tokens(self):
        doc = self.tokens_doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        if os.path.exists("tokens.json"):
            with open("tokens.json", "r", encoding="utf-8") as f:
                tokens = json.load(f)
                self._save_tokens(tokens)
                return tokens
        return None

    def _save_tokens(self, tokens):
        self.tokens_doc_ref.set(tokens)

    def _refresh_access_token(self, refresh_token):
        url = "https://accounts.secure.freee.co.jp/public_api/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            new_tokens = response.json()
            self._save_tokens(new_tokens)
            print("トークンをリフレッシュしました。")
            return new_tokens["access_token"]
        return None

    def fetch_with_auth(self, url, params=None):
        tokens = self._get_tokens()
        if not tokens: return None
        headers = {"Authorization": f"Bearer {tokens['access_token']}", "FREEE-VERSION": "2022-04-01"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 401:
            new_access_token = self._refresh_access_token(tokens["refresh_token"])
            if new_access_token:
                headers["Authorization"] = f"Bearer {new_access_token}"
                response = requests.get(url, headers=headers, params=params)
        return response

    def fetch_freee_transactions(self, days=30):
        url = "https://api.freee.co.jp/api/1/wallet_txns"
        params = {
            "company_id": self.company_id,
            "walletable_type": "bank_account",
            "walletable_id": self.walletable_id,
            "start_date": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        response = self.fetch_with_auth(url, params=params)
        if response and response.status_code == 200:
            return response.json().get("wallet_txns", [])
        return []

    def get_walletable_info(self):
        url = f"https://api.freee.co.jp/api/1/walletables"
        params = {"company_id": self.company_id}
        response = self.fetch_with_auth(url, params=params)
        if response and response.status_code == 200:
            wallets = response.json().get("walletables", [])
            target_id = str(self.walletable_id).strip()
            return next((w for w in wallets if str(w["id"]) == target_id), {})
        return {}

    def export_to_sheets(self):
        """Firestoreから最新の明細リストを読み込み、Googleスプレッドシートへ書き出す"""
        if not self.spreadsheet_id:
            print("SPREADSHEET_ID が設定されていないためスキップします。")
            return

        try:
            # 認証 (スプレッドシートとドライブのスコープを明示的に指定)
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials, _ = google.auth.default(scopes=scopes)
            gc = gspread.authorize(credentials)
            sh = gc.open_by_key(self.spreadsheet_id)
            worksheet = sh.get_worksheet(0)

            # Firestoreから全件取得 (日付の昇順: 通帳形式)
            docs = self.db.collection("companies").document(str(self.company_id)) \
                          .collection("bank_accounts").document(str(self.walletable_id)) \
                          .collection("transactions").order_by("date", direction=firestore.Query.ASCENDING).stream()
            
            rows = [["ID", "日付", "摘要", "金額", "残高", "区分", "消込状況", "マッチングID", "Firestore更新日"]]
            for doc in docs:
                d = doc.to_dict()
                amount = d.get("amount", 0)
                # expense (出金) の場合は金額をマイナスにする
                if d.get("entry_side") == "expense":
                    amount = -abs(amount)
                
                rows.append([
                    doc.id,
                    d.get("date", ""),
                    d.get("description", ""),
                    amount,
                    d.get("balance", 0),
                    d.get("entry_side", ""), # 収支区分
                    d.get("matching_status", "unmatched"),
                    d.get("matched_invoice_id", ""),
                    d.get("updated_at").strftime("%Y-%m-%d %H:%M:%S") if d.get("updated_at") else ""
                ])
            
            # シートのクリアと更新
            worksheet.clear()
            worksheet.update(rows, "A1")
            print(f"スプレッドシート ({sh.title}) を更新しました（{len(rows)-1}件）。")
        except Exception as e:
            import traceback
            print(f"スプレッドシート更新エラー: {e}")
            traceback.print_exc()

    def send_discord_notification(self, count, balance, last_sync_raw, app_time):
        if not self.webhook_url: return
        if last_sync_raw:
            formatted_sync = last_sync_raw.replace('T', ' ').split('+')[0].split('.')[0]
        else:
            formatted_sync = "不明"

        content = (
            f"✅ **デジタル通帳 同期完了**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🏢 **事業所**: {self.company_name}\n"
            f"🏦 **対象口座**: {self.service_name}\n"
            f"📥 **同期明細**: {count} 件\n"
            f"💰 **最新残高**: {balance:,} 円\n"
            f"🕒 **銀行同期**: {formatted_sync}\n"
            f"🚀 **アプリ更新**: {app_time}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🟢 [Spreadsheet](<https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}>)\n"
            f"📊 [Firestore DB](<https://console.cloud.google.com/firestore/data?project={self.project_id}>)\n"
            f"🔗 [freee ログイン](<https://secure.freee.co.jp/>)\n"
            f"🛠️ [GitHub Repo](<https://github.com/zecu32/freee-gcp-digital-passbook>)"
        )
        payload = {"content": content}
        requests.post(self.webhook_url, json=payload)

    def sync_to_firestore(self, transactions):
        if not transactions: return 0
        batch = self.db.batch()
        count = 0
        for txn in transactions:
            txn_id = str(txn["id"])
            doc_ref = self.db.collection("companies").document(str(self.company_id)) \
                             .collection("bank_accounts").document(str(self.walletable_id)) \
                             .collection("transactions").document(txn_id)
            batch.set(doc_ref, {
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
            }, merge=True)
            count += 1
            if count % 500 == 0:
                batch.commit()
                batch = self.db.batch()
        batch.commit()
        return count

    def run(self):
        app_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. freee -> Firestore
        txns = self.fetch_freee_transactions()
        count = self.sync_to_firestore(txns)
        
        # 2. Firestore -> スプレッドシート
        self.export_to_sheets()
        
        # 3. 通知用情報の整理
        wallet_info = self.get_walletable_info()
        balance = wallet_info.get("walletable_balance")
        if balance is None:
            balance = txns[0].get("balance", 0) if txns else 0
        last_sync = wallet_info.get("last_synced_at") or wallet_info.get("update_date")
        if not last_sync and txns:
            last_sync = txns[0].get("date")
            
        # 4. 通知送信
        self.send_discord_notification(count, balance, last_sync, app_time)
        print(f"全工程完了: {count}件同期済み")

def sync_digital_passbook(request=None):
    sync_app = DigitalPassbookSync()
    sync_app.run()
    return "OK", 200

if __name__ == "__main__":
    sync_digital_passbook()
