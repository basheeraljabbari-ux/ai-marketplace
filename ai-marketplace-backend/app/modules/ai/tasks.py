"""
مهام الـ Background Queue. تُنفَّذ بواسطة RQ worker منفصل عن عملية FastAPI الرئيسية
(نفس Process/مشروع الكود، لكن worker process مختلف: `rq worker` — راجع README).

هذا الملف مصمم عمداً بدون أي import من app.core.database بشكل مباشر بالتوقيع،
لتسهيل نقله لمشروع مستقل لاحقاً لو انفصلت خدمة الـ AI فعلياً.
"""
import asyncio
import uuid

from app.core.config import get_settings

settings = get_settings()

# فوق هذي العتبة نسند الفئة تلقائياً؛ تحتها نخزّن الاقتراحات وتبقى category_id
# فاضية عشان الواجهة تعرضها كأزرار اختيار سريع. 0.6 وسط عملي: عالي كفاية إن
# الإسناد الخاطئ نادر، وواطي كفاية إن الحالات الواضحة ما تجبر المستخدم على
# خطوة يدوية بلا داعي.
CATEGORY_AUTO_ASSIGN_THRESHOLD = 0.6


def get_ai_provider():
    if settings.AI_PROVIDER == "mock":
        from app.modules.ai.mock_provider import MockAIProvider
        return MockAIProvider()
    elif settings.AI_PROVIDER == "anthropic":
        from app.modules.ai.anthropic_provider import AnthropicAIProvider
        return AnthropicAIProvider()
    else:
        raise ValueError(f"Unknown AI_PROVIDER: {settings.AI_PROVIDER}")


def run_ai_generation_job(listing_id: str, image_urls: list[str], condition: str) -> dict:
    """Entry point اللي يناديه RQ worker (sync wrapper حول async logic).

    ملاحظة مهمة: لا تضيف باراميتر اسمه job_id هنا — RQ يحجز job_id ككلمة مفتاحية
    خاصة فيه بـ queue.enqueue() (يستخدمها لتحديد ID الـ Job نفسه) وما توصل للدالة
    أبداً، فتطلع TypeError: missing 1 required positional argument: 'job_id'.
    """
    return asyncio.run(_run_ai_generation_job_async(listing_id, image_urls, condition))


async def _run_ai_generation_job_async(listing_id: str, image_urls: list[str], condition: str) -> dict:
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select

    # نستورد كل الـ models قبل أي عملية DB — نفس مبدأ app/main.py و alembic/env.py
    # و tests/conftest.py. الفرق هنا إن الـ RQ worker عملية (process) منفصلة تماماً
    # عن FastAPI، فاستيرادات main.py ما توصله أبداً؛ وبدونها SQLAlchemy يفشل بحل
    # ForeignKey زي listings.seller_id -> users.id لأن كلاس User أصلاً غير محمّل
    # بالـ registry حق هذي العملية.
    from app.modules.geo.models import Country, City  # noqa
    from app.modules.users.models import User  # noqa
    from app.modules.categories.models import Category  # noqa
    from app.modules.listings.models import Listing, ListingImage, ListingAIMetadata  # noqa
    from app.modules.messaging.models import Conversation, Message  # noqa
    from app.modules.favorites.models import Favorite  # noqa
    from app.modules.admin.models import AuditLog  # noqa

    provider = get_ai_provider()
    result = await provider.analyze_and_generate(image_urls, condition)

    async with AsyncSessionLocal() as db:
        listing = await db.get(Listing, uuid.UUID(listing_id))
        if not listing:
            return {"status": "failed", "error": "listing not found"}

        listing.title = result.title
        listing.description = result.description
        listing.is_ai_generated = True
        if result.suggested_price_min:
            listing.price = result.suggested_price_min  # قيمة أولية — المستخدم يعدلها بالمراجعة

        resolved = await _resolve_category_suggestions(db, result.category_suggestions)

        # الإسناد التلقائي فقط لما الأعلى ثقة يتجاوز العتبة.
        top = resolved[0] if resolved else None
        auto_assigned = bool(top and top["confidence"] >= CATEGORY_AUTO_ASSIGN_THRESHOLD)
        if auto_assigned:
            listing.category_id = uuid.UUID(top["category_id"])

        db.add(ListingAIMetadata(
            listing_id=listing.id,
            detected_brand=result.detected_brand,
            detected_color=result.detected_color,
            suggested_price_min=result.suggested_price_min,
            suggested_price_max=result.suggested_price_max,
            ai_confidence=result.confidence,
            raw_ai_response=result.raw_response,
            # نخزّنها دائماً حتى لو أُسندت الفئة تلقائياً — تفيد لمراجعة جودة النموذج،
            # ولو غيّر المستخدم الفئة يدوياً بعدين نعرف شنو كانت البدائل.
            category_suggestions=resolved or None,
        ))
        await db.commit()

    # المفاتيح الإضافية آمنة: القارئ الوحيد (get_ai_job_status) يقرأ listing_id فقط.
    # تفيد بتشخيص الـ worker لأن مخرجاته مو ظاهرة بأي مكان ثاني.
    return {
        "status": "done",
        "listing_id": listing_id,
        "category_assigned": auto_assigned,
        "suggestions": len(resolved),
    }


async def _resolve_category_suggestions(db, suggestions: list[dict]) -> list[dict]:
    """يحوّل [{"slug","confidence"}] لـ [{"slug","category_id","name_en","confidence"}].

    أي slug ما يقابله صف Category حقيقي يُرمى بصمت — النموذج ممكن يرجع slug قديم
    أو مخترع، وما نبي إسناد فئة غير موجودة ولا اقتراح ما ينضغط بالواجهة.
    الترتيب التنازلي بالثقة محفوظ لأن العنصر الأول هو اللي تقرأه عتبة الإسناد.
    """
    if not suggestions:
        return []

    # استيراد محلي — نفس سبب الاستيرادات المحلية بالدالة فوق (عملية الـ worker منفصلة).
    from sqlalchemy import select
    from app.modules.categories.models import Category

    slugs = [s["slug"] for s in suggestions]
    rows = (await db.execute(select(Category).where(Category.slug.in_(slugs)))).scalars().all()
    by_slug = {row.slug: row for row in rows}

    resolved = []
    for suggestion in suggestions:
        category = by_slug.get(suggestion["slug"])
        if not category:
            continue
        resolved.append({
            "slug": category.slug,
            "category_id": str(category.id),  # str عشان JSONB — UUID مو serializable
            "name_en": category.name_en,
            "confidence": suggestion["confidence"],
        })
    return resolved
