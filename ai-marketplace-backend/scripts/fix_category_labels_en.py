"""
إصلاح لمرة واحدة: يوفّق attributes_schema للفئات الموجودة بقاعدة البيانات مع
التعريف الكامل الموجود بـ scripts/seed.py — يضيف label_en، ويترجم خيارات الـ
select، ويكتب الحقول الناقصة كاملة لو الفئة أصلاً بلا schema.

تشغيل مرة وحدة: python -m scripts.fix_category_labels_en

آمن للتكرار (idempotent): يعدّ ويحدّث فقط الفئات اللي تغيّرت فعلاً.
يطبع تفصيل كل فئة عشان لو ما تغيّر شي يبيّن السبب بدل ما يطلع رقم مجرّد.
"""
import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal

# نفس مبدأ app/main.py و alembic/env.py: هذا السكربت عملية منفصلة، فلازم كل
# الـ models تكون محمّلة بالـ registry قبل أي عملية DB وإلا تفشل حلّ الـ ForeignKeys.
from app.modules.geo.models import Country, City  # noqa
from app.modules.users.models import User  # noqa
from app.modules.categories.models import Category  # noqa
from app.modules.listings.models import Listing, ListingImage, ListingAIMetadata  # noqa
from app.modules.messaging.models import Conversation, Message  # noqa
from app.modules.favorites.models import Favorite  # noqa
from app.modules.admin.models import AuditLog  # noqa

# التعريف الكامل المقصود — نسخة طبق الأصل من scripts/seed.py.
# أي تعديل هناك لازم ينعكس هنا (والعكس).
FIELDS_BY_SLUG = {
    "electronics": [
        {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": True, "searchable": True},
        {"key": "condition_detail", "label_ar": "تفاصيل الحالة", "label_en": "Condition details", "type": "text", "required": False},
    ],
    "cars": [
        {"key": "brand", "label_ar": "الماركة", "label_en": "Brand", "type": "text", "required": True, "searchable": True},
        {"key": "year", "label_ar": "سنة الصنع", "label_en": "Year", "type": "number", "required": True, "filterable": True, "min": 1990, "max": 2026},
        {"key": "transmission", "label_ar": "ناقل الحركة", "label_en": "Transmission", "type": "select", "options": ["Automatic", "Manual"], "filterable": True},
        {"key": "mileage_km", "label_ar": "الممشى (كم)", "label_en": "Mileage (km)", "type": "number", "required": False, "filterable": True},
    ],
    "furniture": [
        {"key": "material", "label_ar": "الخامة", "label_en": "Material", "type": "text", "required": False},
    ],
}


def _existing_fields(schema) -> list[dict]:
    """يستخرج قائمة الحقول من الـ schema مهما كان شكلها المخزّن.
    الشكل المتوقع {"fields": [...]}، لكن نتعامل كمان مع list خام أو قيمة فاضية."""
    if isinstance(schema, list):
        return [f for f in schema if isinstance(f, dict)]
    if isinstance(schema, dict):
        fields = schema.get("fields")
        if isinstance(fields, list):
            return [f for f in fields if isinstance(f, dict)]
    return []


def _merge_fields(existing: list[dict], desired: list[dict]) -> list[dict]:
    """يبني قائمة الحقول النهائية: يحافظ على أي خصائص إضافية موجودة بالـ DB
    ويفرض فوقها التعريف المقصود (label_en، options المترجمة، ...)."""
    by_key = {f.get("key"): f for f in existing if f.get("key")}
    merged = []
    for want in desired:
        current = by_key.get(want["key"])
        merged.append({**current, **want} if current else dict(want))
    # أي حقل موجود بالـ DB ومو ضمن التعريف نخليه كما هو بدل ما نحذفه
    extra = [f for f in existing if f.get("key") not in {w["key"] for w in desired}]
    return merged + extra


async def fix_category_labels() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Category).where(Category.slug.in_(list(FIELDS_BY_SLUG))))
        categories = result.scalars().all()

        found = {c.slug for c in categories}
        for slug in FIELDS_BY_SLUG:
            if slug not in found:
                print(f"  {slug}: NOT FOUND in database — no row with this slug")

        updated = 0
        for category in categories:
            desired = FIELDS_BY_SLUG[category.slug]
            schema = category.attributes_schema
            existing = _existing_fields(schema)
            merged = _merge_fields(existing, desired)

            if merged == existing:
                print(f"  {category.slug}: already correct ({len(existing)} field(s)) — no change")
                continue

            # إعادة إسناد الـ dict كامل ضرورية: تعديل JSONB بمكانه ما يعلّم
            # الحقل كـ dirty، فالـ commit يطلع بلا أي UPDATE.
            base = schema if isinstance(schema, dict) else {}
            category.attributes_schema = {**base, "fields": merged}
            updated += 1
            print(
                f"  {category.slug}: {len(existing)} field(s) in DB -> {len(merged)} after merge "
                f"(stored shape: {type(schema).__name__})"
            )

        await db.commit()
        print(f"Done. {updated} categories updated.")


if __name__ == "__main__":
    asyncio.run(fix_category_labels())
