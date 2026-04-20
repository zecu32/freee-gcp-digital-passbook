# freee-gcp-digital-passbook

銀行（広島銀行など）の入出金明細を freee API 経由で取得し、GCP (Cloud Firestore) 上にデジタル通帳を構築するプロジェクトです。

## 1. セットアップ手順

### 環境変数の設定
`.env.example` を参考に `.env` ファイルを作成し、以下の情報を設定してください。

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
```

### 認証・初期化
1. **認可URLの生成**:
   ```bash
   uv run authorize_freee.py
   ```
   表示されたURLをブラウザで開き、承認して「認可コード」を取得します。

2. **トークンの取得**:
   ```bash
   uv run get_token.py <コピーした認可コード>
   ```
   `tokens.json` が生成されます。

### 同期の実行
```bash
uv run main.py
```
freeeから明細が取得され、Firestoreに同期されます。

## 2. 技術スタック
- **Language**: Python (uv)
- **Database**: Google Cloud Firestore
- **API**: freee App Store API (OAuth 2.0)

## 3. 構成
- `main.py`: メイン同期ロジック
- `spec.md`: 詳細なデータ設計とフロー
- `tests/`: 開発中に使用した調査用スクリプト群