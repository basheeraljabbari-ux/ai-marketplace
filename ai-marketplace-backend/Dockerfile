FROM python:3.12-slim

WORKDIR /app

# مكتبات نظام مطلوبة لـ Pillow وpsycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Railway/Render يشغّلون هذا الـ CMD مباشرة (بدون docker-compose)، فلازم الـ migration
# تصير هنا وقت الإقلاع بدل الاعتماد على docker-compose command override.
# $PORT توفّرها منصات الاستضافة تلقائياً؛ نستخدم 8000 كـ fallback للتشغيل المحلي.
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
