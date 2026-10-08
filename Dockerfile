FROM python:3.11-slim

# System dependencies (MySQL client ke liye)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements install karo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Poora project copy karo
COPY . .

# Static files collect karo
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Server chalao
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]