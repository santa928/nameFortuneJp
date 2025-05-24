# 姓名判断アプリケーション

[![CI/CD Pipeline](https://github.com/yourusername/nameFortuneJp/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/nameFortuneJp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/yourusername/nameFortuneJp/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/nameFortuneJp)
[![Security Rating](https://img.shields.io/badge/security-A-green)](https://github.com/yourusername/nameFortuneJp/security)

複数の姓名判断サイトの結果を統合分析するWebアプリケーションです。

## 機能

1. 姓名判断
   - 姓と名を入力して運勢を判定
   - 複数サイトからの結果を統合表示
   - 詳細な運勢解説
   - 運勢スコアの計算
     - enamae.net
       - 大吉：100点
       - 特殊格：90点
       - 吉：80点
       - 吉凶混合：60点
       - 凶：40点
       - 大凶：20点
     - namaeuranai.biz
       - 大大吉：100点
       - 大吉：90点
       - 吉：80点
       - 凶：40点
       - 大凶：20点

2. 画数パターン分析
   - 指定した文字数の全パターンを分析
   - リアルタイムの進捗表示
   - 結果のJSON形式での保存
   - 各パターンの運勢スコア計算
     - enamae.net：天格、人格、地格、外格、総格、三才配置の平均スコア
     - namaeuranai.biz：天格、人格、地格、外格、総格、仕事運、家庭運の平均スコア
     - 総合スコア：両サイトのスコアの平均値

## 技術スタック

- **フロントエンド**：HTML, CSS, JavaScript
- **バックエンド**：Python 3.11+, Flask
- **データベース**：SQLite, ファイルシステム（JSON）
- **コンテナ化**：Docker, docker-compose
- **CI/CD**：GitHub Actions
- **セキュリティ**：Trivy vulnerability scanner
- **テスト**：pytest, coverage.py
- **コード品質**：pre-commit, black, isort, flake8, mypy

## 必要条件

- Docker
- docker-compose

## インストール

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/nameFortuneJp.git
cd nameFortuneJp
```

3. Dockerコンテナの起動
```bash
docker-compose up -d
```

## 使用方法

1. アプリケーションへのアクセス
   - ブラウザで `http://localhost:5000` にアクセス

2. 姓名判断
   - トップページで姓と名を入力
   - 性別を選択
   - 「運勢を判定」ボタンをクリック
   - 各サイトの運勢スコアと総合スコアを確認

3. 画数パターン分析
   - 「画数パターン分析」メニューを選択
   - 姓と文字数を入力
   - 「分析開始」ボタンをクリック
   - 進捗状況を確認しながら結果を待つ
   - 総合スコアの高い順に上位20件の結果を表示

### 3. 画数指定による名前候補生成 (New!)

1. 「名前生成」メニューを選択
2. 名字、性別、各文字の画数を入力
3. 「生成」ボタンをクリック
4. 条件に合致する漢字の名前候補（最大50件）が表示
5. CSV ダウンロードボタンで結果を CSV ファイルとして保存

## データベースへの名前候補データ投入 (CLI)

新機能用の名前候補データを「赤ちゃん命名ガイド」からスクレイピングして SQLite データベースに登録するには、以下の CLI スクリプトを実行します。

```bash
# コンテナを起動中に、別ターミナルで実行
docker-compose exec web python ingest_runner.py \
    --chars 2 \
    --strokes1 8 \
    --strokes2 3 \
    --gender male
```

- `--chars`: 名前の文字数 (1, 2, 3)
- `--strokes1`: 1文字目の画数
- `--strokes2`: 2文字目の画数（`--chars` が2以上の場合必須）
- `--strokes3`: 3文字目の画数（`--chars` が3の場合必須）
- `--gender`: 性別 (`male` または `female`)

初回投入や定期的なバッチ実行で、さまざまな画数パターン・性別パターンを指定してデータを蓄積してください。

```bash
# 例: 1文字 + 女性データを投入
docker-compose exec web python ingest_runner.py --chars 1 --strokes1 5 --gender female
```

## セキュリティ

本プロジェクトでは以下のセキュリティ対策を実装しています：

- **脆弱性スキャン**：Trivyによる依存関係の自動チェック
- **静的解析**：SARIF形式でのセキュリティレポート生成
- **継続的監視**：GitHub Security tabでの脆弱性管理
- **自動アラート**：重要度別セキュリティアラート通知

### セキュリティレポートの確認方法

1. GitHubリポジトリの「Security」タブにアクセス
2. 「Code scanning alerts」で検出された脆弱性を確認
3. 各アラートの詳細と修正提案を確認

