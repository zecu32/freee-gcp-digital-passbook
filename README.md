# freee-gcp-digital-passbook

銀行（広島銀行など）の入出金明細を freee API 経由で取得し、GCP (Cloud Firestore) 上にデジタル通帳を構築するプロジェクトです。
同期完了時には Discord へ最新の残高情報が通知されます。

## 1. セットアップ手順

### 環境変数の設定
`.env` ファイルに以下の情報を設定してください。

```bash
FREEE_CLIENT_ID=XXXX
FREEE_CLIENT_SECRET=XXXX
FREEE_REDIRECT_URI=http://localhost:8000/callback
GCP_PROJECT_ID=your-project-id

# 同期対象の設定
FREEE_COMPANY_ID=12610654
FREEE_COMPANY_NAME=KOMA
FREEE_WALLETABLE_ID=4717432
FREEE_SERVICE_NAME=広島銀行

# 通知設定
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/...
```

### 認証・初期化
1. **認可URLの生成**:
   ```bash
   uv run authorize_freee.py
   ```
2. **トークンの取得**:
   ```bash
   uv run get_token.py <コピーした認可コード>
   ```

### 同期の実行
```bash
uv run main.py
```

## 2. 主な機能
- **自動同期 (Firestore)**: 明細をFirestoreへ自動保存。重複チェック機能付き。
- **Discord通知**: 最新の残高、同期件数、銀行同期時刻を通知。
- **管理ダッシュボード連携**: 通知内のリンクから **freee**, **Firestore**, **GitHub** へ直接アクセス可能。

## 3. 構成
- `main.py`: メイン同期ロジック & Discord通知
- `spec.md`: 詳細なデータ設計とフロー
- `tests/`: 開発中に使用した調査用スクリプト群（バックアップ）