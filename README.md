# Bazo — المشروع الكامل

مجلدين رئيسيين:
- `ai-marketplace-backend/` — FastAPI + PostgreSQL + Redis (35 endpoint، 19 test)
- `ai-marketplace-web/` — React + TypeScript (12 صفحة، build نظيف)

## التشغيل السريع (Docker)
```bash
cp ai-marketplace-backend/.env.example ai-marketplace-backend/.env
docker compose up --build
```
- Backend docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

راجع README.md داخل كل مجلد للتفاصيل الكاملة والتشغيل بدون Docker.
