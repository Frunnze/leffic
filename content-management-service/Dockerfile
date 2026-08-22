FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/src

COPY requirements.txt .
RUN pip install --no-cache-dir "pip<24.1"
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --upgrade six

COPY . .

RUN useradd --system --create-home appuser \
    && mkdir -p /app/files \
    && chown -R appuser /app
USER appuser

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]