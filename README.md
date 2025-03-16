# 姓名判断アプリケーション

複数の姓名判断サイトの結果を統合分析するWebアプリケーションです。

## 機能

1. 姓名判断
   - 姓と名を入力して運勢を判定
   - 複数サイトからの結果を統合表示
   - 詳細な運勢解説

2. 画数パターン分析
   - 指定した文字数の全パターンを分析
   - リアルタイムの進捗表示
   - 結果のJSON形式での保存

## 技術スタック

- フロントエンド：HTML, CSS, JavaScript
- バックエンド：Python 3.8+, Flask
- データベース：ファイルシステム（JSON）
- コンテナ化：Docker, docker-compose

## 必要条件

- Docker
- docker-compose

## インストール

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/nameFortuneJp.git
cd nameFortuneJp
```

2. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
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

3. 画数パターン分析
   - 「画数パターン分析」メニューを選択
   - 姓と文字数を入力
   - 「分析開始」ボタンをクリック
   - 進捗状況を確認しながら結果を待つ

## 開発

1. 開発環境のセットアップ
```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
.\venv\Scripts\activate  # Windows

# 依存パッケージのインストール
pip install -r requirements.txt
```

2. テストの実行
```bash
pytest
```

3. コードスタイルのチェック
```bash
flake8
```

## ライセンス

MIT License

## 貢献

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 注意事項

- このアプリケーションは姓名判断サイトの利用規約に従って使用してください
- スクレイピングの間隔は適切に設定されていますが、過度な使用は避けてください
- 結果は参考程度に留め、最終的な判断は自己責任で行ってください

## 将来の拡張予定

1. 名前生成機能
   - 姓と性別から最適な名前を提案
   - 画数パターンに基づく分析
   - 運勢スコアの計算と表示

2. データ管理機能
   - 結果の履歴管理
   - お気に入り機能
   - 結果の共有機能

3. パフォーマンス最適化
   - キャッシュ機能
   - 非同期処理の改善
   - バッチ処理の導入
