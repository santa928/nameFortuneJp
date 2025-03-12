FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# デバッグ用のコマンドを追加
RUN echo "python test_scraper.py" > /app/run_test.sh && \
    chmod +x /app/run_test.sh

CMD ["flask", "run", "--host=0.0.0.0"] 