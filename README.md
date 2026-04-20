# freee-gcp-digital-passbook (Cloud Edition)

銀行（広島銀行など）の入出金明細を freee API 経由で取得し、GCP (Cloud Firestore) 上にデジタル通帳を構築するプロジェクトです。
Cloud Functions と Cloud Scheduler により、**全自動で毎日 9:00 に同期** が行われます。

## 1. システム構成
- **Cloud Functions**: 同期ロジックの実行
- **Cloud Scheduler**: 毎日 9:00 定期実行タイマー
- **Firestore**: 明細データおよび OAuth トークンの保存
- **Discord**: 実行結果のプッシュ通知

## 2. デプロイ方法
すでにデプロイ済みの場合は、再デプロイ時に以下のコマンドを使用します。
```bash
gcloud functions deploy freee-sync-task --project=my-project-52145-364803 --region=asia-northeast1 --quiet
```

## 3. トークンの管理
お使いの OAuth トークンは Firestore の `/settings/freee_tokens` に保存されており、プログラム実行時に自動リフレッシュされます。特別な操作は不要です。

## 4. 主なファイル
- `main.py`: クラウド実行用のメインプログラム
- `spec.md`: クラウド構成の詳細仕様書
- `.env.yaml`: クラウド環境変数設定