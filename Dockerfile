FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OCR_LANG=por+eng

# Dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    ghostscript \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    ffmpeg \
    gcc \
    libjpeg62-turbo-dev zlib1g-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=7001
EXPOSE 7001

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7001", "main:app"]
