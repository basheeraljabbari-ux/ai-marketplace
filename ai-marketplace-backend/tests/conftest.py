"""
يستورد كل الـ SQLAlchemy models مرة وحدة قبل أي اختبار — يحل مشكلة معروفة:
لو ملف اختبار استورد Model واحد بس (مثلاً Category)، وذاك الـ Model عنده
علاقة (relationship) بنص لـ Model ثاني ما تم استيراده (مثلاً City)،
SQLAlchemy يفشل بتهيئة الـ mappers لأنه ما يلقى الكلاس المرتبط بنفس الـ registry.

هذا الملف نفس مبدأ alembic/env.py بالضبط — يضمن كل الـ models "حاضرة"
بغض النظر عن أي ملف اختبار يشتغل لحاله.
"""
from app.modules.geo.models import Country, City  # noqa
from app.modules.users.models import User  # noqa
from app.modules.categories.models import Category  # noqa
from app.modules.listings.models import Listing, ListingImage, ListingAIMetadata  # noqa
from app.modules.messaging.models import Conversation, Message  # noqa
from app.modules.favorites.models import Favorite  # noqa
from app.modules.admin.models import AuditLog  # noqa

from app.core.rate_limit import limiter

# نطفّي الـ rate limiter بالاختبارات فقط.
#
# AUTH_RATE_LIMIT = "5/minute" مربوط بالـ IP، والاختبارات التكاملية تسجّل 11 مستخدم
# من نفس الـ IP خلال ثواني — فبـ CI كانت /auth/register ترجع 429 بدل 201، وتفشل
# 9 اختبارات بـ KeyError: 'access_token'. الحد نفسه صحيح ولازم يبقى بالإنتاج.
#
# التعطيل هنا وليس بـ app/core/rate_limit.py عن قصد: conftest.py ما ينستورد أبداً
# من التطبيق الحقيقي، فما في طريقة يتسرّب فيها هذا السطر للإنتاج. لو ربطناه بمتغيّر
# بيئة (TESTING=1) بدل هيك، أي ضبط خاطئ للمتغيّر بالإنتاج يلغي الحماية بصمت.
#
# slowapi يقرأ .enabled وقت كل request (مو وقت تطبيق الـ decorator)، فالتعديل هون
# بعد الاستيراد كافي — يتخطّى فحص الحد وحقن headers الـ X-RateLimit سوا.
limiter.enabled = False
