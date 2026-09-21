# AegisX backend image: Python 3.12-slim + requirements → uvicorn app.main:app:8000.
# Help: rebuild after ANY backend change (`docker compose up --build`). Tests ship
# inside (`COPY tests`) but run outside Docker via `python3 -m pytest tests`.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY tests ./tests
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
