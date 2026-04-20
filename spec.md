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
特定の銀行口座に紐づく入出金明細。freeeからの同期データに加え、実務用の消込情報を管理する。

- **ドキュメントID**: freeeの明細ID (`entry_id`) 
- **[A] freee同期フィールド** (プログラムにより自動更新):
    - `date`: string (発生日)
    - `amount`: number (取引金額)
    - `balance`: number (残高)
    - `description`: string (摘要)
    - `entry_side`: string (income/expense)
    - `updated_at`: server_timestamp
- **[B] 実務用メタデータ** (UIやマッチングロジックで管理):
    - `matching_status`: string (`unmatched`, `matched`, `pending`) ※デフォルトは `unmatched`
    - `matched_invoice_id`: string (突合した請求書番号や売掛金ID)
    - `matched_at`: timestamp (突合処理日時)
    - `memo`: string (実務メモ)
    - `reconciled_by`: string (処理担当者)

---

## 2. システム構成 (GCPクラウド)

1. **実行環境 (Cloud Functions)**: `main.py` をホスト。
2. **タイマー (Cloud Scheduler)**: 毎日 9:00 (JST) に実行。
3. **DB (Firestore)**: 明細と実務ステータスを保持。`merge`保存により実務メタデータを保護。
4. **通知 (Discord)**: 同期結果および「未消込件数」などのサマリー通知（予定）。

---

## 3. 実務ワークフロー (売掛金マッチング)

1. **自動取得**: 毎朝、銀行明細が Firestore に自動反映される。
2. **自動推論**: 登録された売掛金IDと金額・日付が一致する場合、自動で `matched_invoice_id` を仮登録。
3. **手動確認**: 管理画面（スプレッドシート形式）で、未消込の明細に対して担当者が請求書を紐付け。
4. **反映**: マッチング完了したデータを元に、将来的に freee 側の消込 API を叩く等の拡張。

## 4. 今後の拡張予定
- **売掛金インポート**: スプレッドシートや別システムから売掛金リストを Firestore へ取り込み。
- **消込管理画面**: 実務担当者がブラウザ上でスプレッドシートのように操作できる UI の構築。
