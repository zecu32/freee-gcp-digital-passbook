# プロジェクト仕様書 (spec.md)

## 1. データベース設計 (Cloud Firestore)

Firestoreの階層構造およびフィールド定義です。

### 階層構造図
```text
/companies/{company_id}
    |-- /bank_accounts/{account_id}
    |       ┗-- /transactions/{transaction_id} (明細データ)
    |
    ┗-- /settings/freee_tokens (OAuthトークン管理)
```

### コレクション詳細

#### (1) `transactions` サブコレクション
特定の銀行口座に紐づく明細。
- **ドキュメントID**: freeeの明細ID (`entry_id`) 
- **主要フィールド**: `date`, `amount`, `balance`, `description`, `entry_side`, `service_name`, `company_name`, `updated_at`

#### (2) `settings/freee_tokens` (トークン管理)
- **フィールド**: `access_token`, `refresh_token`, `expires_in` 等
- **役割**: APIの認可情報を永続化。期限切れ時に自動リフレッシュされる。

---

## 2. システム構成 (GCPクラウド)

1. **実行環境 (Cloud Functions)**: `main.py` をホスト。HTTPトリガーで起動。
2. **タイマー (Cloud Scheduler)**: 毎日 9:00 (JST) に実行URLをキック。
3. **DB (Firestore)**: 明細データとトークン情報を一元管理。
4. **通知 (Discord)**: 実行結果をリアルタイム通知。

---

## 3. 運用フロー
- **全自動**: 毎日 9:00 に自動実行され、Discord に通知が届く。
- **保守**: 万が一トークンが無効になった場合は、再度 `authorize_freee.py` -> `get_token.py` をローカルで実行することで Firestore 内のトークンが更新される。
