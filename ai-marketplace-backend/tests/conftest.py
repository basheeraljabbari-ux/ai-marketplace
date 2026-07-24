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
