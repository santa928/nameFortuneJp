# マルチステージビルドを使用
FROM python:3.11-slim as builder

# セキュリティ: 非rootユーザーでの実行
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# システムの依存関係をインストール（キャッシュ効率化）
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Pythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 本番ステージ
FROM python:3.11-slim

# 非rootユーザーを作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 必要なシステムパッケージのみインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ビルダーステージから依存関係をコピー
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# アプリケーションファイルをコピー
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser tests/ ./tests/

# 静的ファイル用のディレクトリを作成
RUN mkdir -p /app/static && chown -R appuser:appuser /app

# 非rootユーザーに切り替え
USER appuser

# ポートを公開
EXPOSE 5000

# アプリケーションを実行
CMD ["python", "-m", "app.main"]

# より詳細なヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:5000/healthz || exit 1 