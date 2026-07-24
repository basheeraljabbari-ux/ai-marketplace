"""
إصلاح لمرة واحدة: الفئات المزروعة قبل إضافة label_en عندها label_ar فقط،
فالواجهة تعرض تسميات عربية رغم إن الموقع كله إنجليزي. هذا السكربت يضيف
label_en (ويترجم خيارات الـ select) للفئات الموجودة فعلياً بقاعدة البيانات،
مطابقة بالـ slug. seed.py صار يكتب label_en أصلاً — هذا للبيانات القديمة فقط.

تشغيل مرة وحدة: python -m scripts.fix_category_labels_en

آمن للتكرار (idempotent): يعدّ فقط الفئات اللي تغيّرت فعلاً.
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

# نفس القيم الموجودة بـ scripts/seed.py بالضبط — أي تعديل هناك لازم ينعكس هنا.
LABELS_EN = {
    "electronics": {
        "brand": "Brand",
        "condition_detail": "Condition details",
    },
    "cars": {
        "brand": "Brand",
        "year": "Year",
        "transmission": "Transmission",
        "mileage_km": "Mileage (km)",
    },
    "furniture": {
        "material": "Material",
    },
}

# خيارات الـ select تُخزَّن كقيم فعلية، فترجمتها تغيّر البيانات نفسها لا التسمية فقط.
OPTIONS_EN = {
    ("cars", "transmission"): ["Automatic", "Manual"],
}


async def fix_category_labels() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Category).where(Category.slug.in_(list(LABELS_EN))))
        categories = result.scalars().all()

        updated = 0
        for category in categories:
            labels = LABELS_EN[category.slug]
            schema = category.attributes_schema or {}
            fields = schema.get("fields") or []

            new_fields = []
            changed = False
            for field in fields:
                new_field = dict(field)
                key = new_field.get("key")

                label_en = labels.get(key)
                if label_en and new_field.get("label_en") != label_en:
                    new_field["label_en"] = label_en
                    changed = True

                options_en = OPTIONS_EN.get((category.slug, key))
                if options_en and new_field.get("options") != options_en:
                    new_field["options"] = options_en
                    changed = True

                new_fields.append(new_field)

            if changed:
                # إعادة إسناد الـ dict كامل ضرورية: تعديل JSONB بمكانه ما يعلّم
                # الحقل كـ dirty، فالـ commit يطلع بلا أي UPDATE.
                category.attributes_schema = {**schema, "fields": new_fields}
                updated += 1

        await db.commit()
        print(f"Done. {updated} categories updated.")


if __name__ == "__main__":
    asyncio.run(fix_category_labels())
