"""
توسعة الفئات من 3 إلى 12 على قاعدة بيانات شغّالة.

الفكرة: الفئتين القديمتين "cars" و "furniture" تتحدّثان *بمكانهما* (نفس الـ id)
إلى "vehicles" و "home-goods" — عشان الإعلانات المربوطة فيهما تبقى مربوطة ولا
تحتاج أي نقل. باقي الفئات الجديدة تُنشأ لو مو موجودة أصلاً.

تشغيل مرة وحدة: python -m scripts.expand_categories

آمن للتكرار (idempotent): يتخطّى أي slug موجود، ويشتغل صح لو انقطع بالنص.
"""
import asyncio
import uuid

from sqlalchemy import select

from app.core.database import AsyncSessionLocal

# نفس مبدأ app/main.py و alembic/env.py: هذا السكربت عملية منفصلة، فلازم كل
# الـ models تكون محمّلة بالـ registry قبل أي عملية DB وإلا تفشل حلّ الـ ForeignKeys.
from app.modules.geo.models import Country, City  # noqa
from app.modules.users.models import User  # noqa
from app.modules.categories.models import Category
from app.modules.listings.models import Listing, ListingImage, ListingAIMetadata  # noqa
from app.modules.messaging.models import Conversation, Message  # noqa
from app.modules.favorites.models import Favorite  # noqa
from app.modules.admin.models import AuditLog  # noqa

# مصدر الحقيقة الوحيد للتعريفات — مستورد من seed.py عشان ما ينفرط التطابق.
from scripts.seed import CATEGORIES

# الفئات القديمة اللي تتحدّث بمكانها بدل ما تُنشأ من جديد (الـ id ما يتغيّر).
RENAMES = {"cars": "vehicles", "furniture": "home-goods"}

BY_SLUG = {c["slug"]: c for c in CATEGORIES}


async def expand_categories() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Category))
        existing = {c.slug: c for c in result.scalars().all()}

        renamed = created = 0

        # 1) تحديث الفئتين القديمتين بمكانهما
        for old_slug, new_slug in RENAMES.items():
            target = BY_SLUG[new_slug]
            old = existing.get(old_slug)

            if old is None:
                if new_slug in existing:
                    print(f"  {old_slug} -> {new_slug}: already migrated — skipped")
                else:
                    print(f"  {old_slug} -> {new_slug}: old slug NOT FOUND — will be created below")
                continue

            if new_slug in existing:
                # حالة غير متوقّعة: الاثنين موجودين. ما نلمس شي عشان ما نكسر
                # قيد الـ unique، ونترك القرار للبشر.
                print(
                    f"  {old_slug} -> {new_slug}: CONFLICT — both slugs exist "
                    f"(old id={old.id}, new id={existing[new_slug].id}). Skipped, needs manual review."
                )
                continue

            old.name_ar = target["name_ar"]
            old.name_en = target["name_en"]
            old.slug = new_slug
            # إعادة إسناد الـ dict كامل ضرورية: تعديل JSONB بمكانه ما يعلّم
            # الحقل كـ dirty، فالـ commit يطلع بلا أي UPDATE.
            old.attributes_schema = {"fields": target["fields"]}
            existing[new_slug] = old
            renamed += 1
            print(f"  {old_slug} -> {new_slug}: updated in place (id={old.id} unchanged)")

        # 2) إنشاء الباقي
        for category in CATEGORIES:
            slug = category["slug"]
            if slug in existing:
                continue
            db.add(Category(
                id=uuid.uuid4(),
                name_ar=category["name_ar"],
                name_en=category["name_en"],
                slug=slug,
                attributes_schema={"fields": category["fields"]},
            ))
            created += 1
            print(f"  {slug}: created")

        await db.commit()
        print(f"Done. {renamed} renamed in place, {created} created, {len(CATEGORIES)} total expected.")


if __name__ == "__main__":
    asyncio.run(expand_categories())
