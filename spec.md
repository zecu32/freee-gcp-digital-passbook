# プロジェクト仕様書 (spec.md)

## 1. データベース設計 (Cloud Firestore)

Firestoreの階層構造およびフィールド定義です。

### 階層構造図
```text
/companies/{company_id}
    |-- (fields: name, display_name)
    |
    ┗-- /bank_accounts/{account_id}
            |-- (fields: bank_name, type)
            |
            ┗-- /transactions/{transaction_id}
                    |-- (Core Data)
```

### コレクション詳細

#### (1) `transactions` サブコレクション (明細データ)
特定の銀行口座に紐づく明細。自己完結性を高めるため、親のメタデータも保持する。
- **ドキュメントID**: freeeの明細ID (`entry_id`) 
- **フィールド**:
    - `date`: string (発生日: YYYY-MM-DD)
    - `amount`: number (取引金額)
    - `balance`: number (その時点の残高)
    - `description`: string (摘要・内容)
    - `entry_side`: string (`income` または `expense`)
    - `service_name`: string (連携元サービス: 例 `広島銀行`)
    - `company_name`: string (事業所名: 例 `KOMA`)
    - `walletable_id`: number (口座ID)
    - `company_id`: number (事業所ID)
    - `updated_at`: server_timestamp (Firestore更新日時)

---

## 2. API連携および通知フロー

1. **認可初期化**: `authorize_freee.py` で認可URLを発行し、ブラウザで承認。
2. **トークン取得**: 取得したコードを `get_token.py` に渡し、`tokens.json` を生成。
3. **データ同期**: `main.py` を実行。
   - freee APIから最新明細を取得し、Firestoreへ保存。
   - 既存データがある場合は `merge` モードで更新。
4. **Discord通知**: 同期完了後、以下の情報を Discord Webhook へ送信。
   - 同期件数、最新残高、銀行側の最終同期日時。
   - freeeログインおよびリポジトリへのクイックアクセスリンク。

## 3. 同期仕様の注意点
- **銀行同期日時**: APIの制限により、正確な時刻が取得できない場合は「日付」のみを表示する。
- **重複排除**: freeeのユニークIDを使用しているため、何度 `main.py` を実行しても Firestore 内に重複データは作成されない。

## 4. 今後の拡張予定
- **自動同期**: Cloud Scheduler を用いた定期的な `main.py` の実行。
- **フィルタリング通知**: 大額の入出金があった場合のみ強調通知する機能。
