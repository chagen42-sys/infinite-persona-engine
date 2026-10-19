FROM python:3.11-slim

# Install system dependencies for Playwright browsers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        curl \
        git \
        libnss3 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libxshmfence1 \
        libx11-6 \
        libxext6 \
        libxrender1 \
        libxss1 \
        libxtst6 \
        ca-certificates \
        fonts-liberation \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ⭐ THIS installs Chromium inside the container ⭐
RUN python -m playwright install --with-deps

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]