## 2025-10-12

- Removed: 名前生成機能（`/name_generator` UI、`/api/v1/name_candidates` API、関連スクレイピング/DB投入処理、テンプレート、ナビゲーションリンク、環境変数、Compose ボリューム）
- Updated: ドキュメント（要件定義・仕様書・機能一覧・README）から該当箇所を削除/整理
- Removed: SQLite/DB 関連（`names.db`、`DATABASE_PATH`、DBスキーマ記述）
- Chore: docker-compose（test）から DB 変数を削除
- Docs: 仕様書・画数別運勢一覧機能仕様書を「データ保存: JSON」に統一
- QA: UIスモーク（`/` と `/analyze_strokes`）、`/healthz` OK／pytest 10件 pass
