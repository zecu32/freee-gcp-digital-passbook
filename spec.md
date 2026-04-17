# プロジェクト仕様書 (spec.md)

## 1. データベース設計 (Cloud Firestore)

Firestoreの階層構造およびフィールド定義です。

### 階層構造図
```text
/companies/{company_id}
    |-- (fields: name, display_name)
    |
    ┗-- /bank_accounts/{account_id}
            |-- (fields: bank_name, type, last_synced)
            |
            ┗-- /transactions/{transaction_id}
                    |-- (fields: date, amount, description, balance)
```

### コレクション詳細

#### (1) `companies` コレクション
事業所を管理します。
- **ドキュメントID**: freeeの事業所ID (`company_id`)
- **フィールド**:
    - `name`: string (事業所正式名称)
    - `display_name`: string (表示用名称)
    - `updated_at`: timestamp (情報更新日時)

#### (2) `bank_accounts` サブコレクション
特定の事業所に紐づく銀行口座を管理します。
- **ドキュメントID**: freeeの口座ID (`walletable_id`)
- **フィールド**:
    - `bank_name`: string (銀行名、口座名)
    - `walletable_type`: string (例: `bank_account`, `credit_card`)
    - `last_synced_at`: timestamp (最終同期日時)

#### (3) `transactions` サブコレクション
特定の銀行口座に紐づく明細一行一行を管理します。
- **ドキュメントID**: freeeの明細ID (`entry_id`) または一意のハッシュ値
- **フィールド**:
    - `date`: date (発生日)
    - `amount`: number (金額: 入金は正、出金は負)
    - `description`: string (備考・振込先名など)
    - `balance`: number (その時点の残高)
    - `created_at`: timestamp (Firestoreに保存された日時)

---

## 2. API連携フロー

1. freee API からアクセストークンを使い事業所一覧を取得。
2. 対象の事業所IDを指定して、銀行口座（Walletables）一覧を取得。
3. 口座IDを指定して、入出金明細を取得。
4. 取得した明細を Firestore の `transactions` へ保存（重複チェックを行う）。
