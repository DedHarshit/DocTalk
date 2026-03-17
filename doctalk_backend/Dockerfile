FROM python:3.11-slim

WORKDIR /app

COPY doctalk_backend/backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY doctalk_backend/backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]