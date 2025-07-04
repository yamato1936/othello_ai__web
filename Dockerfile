FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 起動スクリプトを作成し、実行権限を付与
# ▼▼▼ このスクリプトを、より堅牢なものに修正 ▼▼▼
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'echo "--- Starting Celery Worker in background ---"' >> /app/start.sh && \
    echo 'celery -A tasks.celery worker --loglevel=info &' >> /app/start.sh && \
    echo 'echo "--- Starting Gunicorn Web Server in foreground ---"' >> /app/start.sh && \
    echo 'gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app' >> /app/start.sh && \
    chmod +x /app/start.sh

# コンテナ起動時に、作成した起動スクリプトを実行
CMD ["/app/start.sh"]