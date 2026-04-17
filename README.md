
1. プロジェクトの目的
銀行（広島銀行など）の入出金明細をfreee API経由で取得し、GCP（Google Cloud Platform）上に「デジタル通帳」を再現する。
2. 開発環境（IDE）と技術スタック
IDE: Google Antigravity (次世代IDE)
言語: Python（プロトタイプ） → Rust（堅牢化・本番運用）
インフラ: GCP (Cloud Functions, Firestore, Cloud Scheduler, Secret Manager)
管理: Git / GitHub