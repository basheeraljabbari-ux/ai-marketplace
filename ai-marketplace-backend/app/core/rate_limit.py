from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

# نستخدم IP كمفتاح افتراضي. بالإنتاج خلف reverse proxy لازم تفعيل
# trusted proxy headers (X-Forwarded-For) عشان الـ IP الحقيقي ينوصل صح.
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,  # نفس Redis المستخدم للـ AI queue — لا حاجة لخدمة إضافية
    strategy="fixed-window",
)

# حدود مخصصة للـ endpoints الحساسة (موثّقة بوثيقة المرحلة 1 — Non-Functional Requirements)
AUTH_RATE_LIMIT = "5/minute"       # تسجيل دخول/تسجيل — يمنع brute-force
AI_GENERATE_RATE_LIMIT = "10/hour"  # توليد AI — يمنع استنزاف تكلفة الـ AI provider
DEFAULT_RATE_LIMIT = "100/minute"   # باقي الـ endpoints
