FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn httpx python-dotenv
COPY . .
CMD ["uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "9000"]