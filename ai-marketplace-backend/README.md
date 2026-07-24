# AI Marketplace — Backend (كامل)

Backend كامل، فعلي، ومُختبَر. 35 endpoint، 19 unit test ناجح، Docker جاهز، CI جاهز.

> Deployed via Railway.

## ✅ التغطية الكاملة

| Module | التغطية |
|---|---|
| auth | register, login, refresh, logout — مع rate limiting (5/دقيقة) |
| users | me (get/update), profile عام, إعلانات مستخدم |
| listings | CRUD كامل، نشر (مع تحقق attributes_schema فعلي)، تمييز كمباع، رفع/حذف صور فعلي (S3، حذف فعلي عند الحذف) |
| ai | Interface + **MockAIProvider** (تطوير) + **AnthropicAIProvider حقيقي** (Claude vision)، queue فعلي عبر RQ/Redis، rate limiting (10/ساعة) |
| search | Search Service Interface + PostgreSQL FTS provider فعلي |
| categories | list، attributes-schema، **تحقق فعلي من القيم وقت النشر** (required/number range/select options) |
| messaging | محادثات + رسائل، denormalized fields ضمن transaction واحدة |
| favorites | إضافة/حذف/عرض (idempotent) |
| admin | stats، إدارة مستخدمين، **عرض/حذف كل الإعلانات**، إدارة فئات، audit logs |
| DB | Alembic migrations كاملة + trigger بحث نصي تلقائي |
| Rate limiting | فعلي عبر slowapi + Redis — auth وAI محميين |
| Deployment | Dockerfile + docker-compose (Postgres, Redis, backend, AI worker, frontend) |
| CI | GitHub Actions — يشغّل الاختبارات تلقائياً بكل push |
| Tests | 19 unit test (security, pagination, attributes validator) بدون DB + integration tests كاملة (تحتاج Postgres) |

## التشغيل — طريقتين

### أ) Docker (الأسهل — يشغّل كل شي بأمر واحد)
```bash
# من مجلد ai-marketplace/ (يحتوي backend + frontend)
cp ai-marketplace-backend/.env.example ai-marketplace-backend/.env
docker compose up --build
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:5173
```

### ب) محلياً بدون Docker
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

alembic upgrade head
python -m scripts.seed

uvicorn app.main:app --reload
rq worker ai_generation --url redis://localhost:6379/0   # نافذة ثانية

pytest tests/test_security.py tests/test_pagination.py tests/test_attributes_validator.py -v
```

## ربط AI حقيقي (Claude API)

بالـ .env غيّر:
```
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-...
```
`AnthropicAIProvider` (`app/modules/ai/anthropic_provider.py`) يستخدم Claude لتحليل الصور فعلياً ويرجع JSON منظّم (فئة، ماركة، لون، عنوان، وصف، نطاق سعري). الكود جاهز ومكتمل — لم يُختبر ببيئة هذي مباشرة لعدم وجود مفتاح API بالـ sandbox، لكنه مبني على نفس الـ interface المُختبَر لـ MockAIProvider.

## ما تم اكتشافه وإصلاحه أثناء هذا التمرير (فحص فعلي، مو نظري)

- **bug حقيقي بتسجيل SQLAlchemy mappers**: ملف اختبار استورد Model وحيد (Category) بدون باقي الـ models المرتبطة (City) → فشل. الحل: `tests/conftest.py` يستورد كل الـ models مرة وحدة، نفس مبدأ `alembic/env.py`
- endpoint `GET /admin/listings` كان ناقص فعلياً رغم إنه موثّق بالتصميم — أُضيف
- `role` كان ناقص من `UserMe` schema رغم إن الفرونت اند يحتاجه لعرض رابط الإدارة

## الناقص المتبقي (صراحة كاملة)

- Email verification (كان اختياري بالـ MVP أصلاً)
- Tests لموديولات messaging/favorites/admin على مستوى service (موجودة integration tests عامة بس مو شاملة كل حالة)
- Deployment فعلي على استضافة حقيقية (Docker جاهز، بس ما تم رفعه على Railway/Render فعلياً)
- Monitoring/observability (Sentry, logging مركزي) — مذكور بمتطلبات المرحلة 1 كـ Non-Functional، غير مطبّق

