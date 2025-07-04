# 1. ベースとなる公式のPythonイメージを選択
FROM python:3.12-slim

# 2. コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 3. パフォーマンス向上のため、まずライブラリの定義ファイルだけをコピー
COPY requirements.txt .

# 4. 必要なライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# 5. アプリケーションの全てのコードを作業ディレクトリにコピー
COPY . .

# 6. 起動スクリプトを作成
# このスクリプトが、WebサーバーかWorkerかによって起動コマンドを切り替える
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'if [ "$SERVICE_TYPE" = "worker" ]; then' >> /app/start.sh && \
    echo '  celery -A tasks.celery worker --loglevel=info' >> /app/start.sh && \
    echo 'else' >> /app/start.sh && \
    echo '  gunicorn --bind 0.0.0.0:$PORT app:app' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    chmod +x /app/start.sh

# 7. このコンテナが起動したときに、作成した起動スクリプトを実行する
# PORTはRenderが自動で設定してくれる
CMD ["/app/start.sh"]
