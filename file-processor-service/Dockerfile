FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    antiword \
    unrtf \
    poppler-utils \
    tesseract-ocr \
    flac \
    ffmpeg \
    lame \
    libmad0 \
    libsox-fmt-mp3 \
    sox \
    libjpeg-dev \
    swig \
    python3-distutils \
    libreoffice \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install "pip<24.1"
RUN pip install -r requirements.txt
RUN pip install --upgrade six

COPY . .
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]