FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY trip_master/ trip_master/
RUN pip install --no-cache-dir .

COPY . .

CMD ["python", "main.py"]
