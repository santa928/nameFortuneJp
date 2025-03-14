FROM python:3.9-slim

WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# 静的ファイル用のディレクトリを作成
RUN mkdir -p /app/static

# ポートを公開
EXPOSE 5000

# アプリケーションを実行
CMD ["python", "app.py"] 