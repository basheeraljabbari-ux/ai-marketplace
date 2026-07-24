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
    from app.modules.listings.models import Listing, ListingAIMetadata
    from sqlalchemy import select

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

        db.add(ListingAIMetadata(
            listing_id=listing.id,
            detected_brand=result.detected_brand,
            detected_color=result.detected_color,
            suggested_price_min=result.suggested_price_min,
            suggested_price_max=result.suggested_price_max,
            ai_confidence=result.confidence,
            raw_ai_response=result.raw_response,
        ))
        await db.commit()

    return {"status": "done", "listing_id": listing_id}
