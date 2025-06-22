FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY README.md .

ENV PYTHONPATH=/app/src
ENV DB_PATH=/data/ais.db

CMD ["uvicorn", "sailtrack.api:app", "--host", "0.0.0.0", "--port", "8000"]
