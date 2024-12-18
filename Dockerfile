# ベースイメージ
FROM python:3.9-slim

# 作業ディレクトリ
WORKDIR /app

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential &&     rm -rf /var/lib/apt/lists/*

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードコピー
COPY . .

# エントリポイント
CMD ["python", "server.py"]
