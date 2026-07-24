from uuid import UUID

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.listings.models import Listing
from app.modules.search.interface import SearchProvider, SearchFilters, SearchResult


class PostgresSearchProvider(SearchProvider):
    """يعتمد على عمود listings.search_vector (TSVECTOR) اللي يُحدَّث تلقائياً
    بـ DB trigger عند INSERT/UPDATE — راجع alembic migration.
    لا نحتاج فهرسة يدوية هنا؛ index_listing/remove_listing موجودة فقط
    لإرضاء الـ interface والتوافق المستقبلي مع OpenSearchProvider."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(self, query: str | None, filters: SearchFilters, page: int, limit: int) -> SearchResult:
        stmt = select(Listing.id).where(Listing.status == "active", Listing.deleted_at.is_(None))

        if query:
            stmt = stmt.where(Listing.search_vector.op("@@")(func.plainto_tsquery("simple", query)))
        if filters.city_id:
            stmt = stmt.where(Listing.city_id == filters.city_id)
        if filters.category_id:
            stmt = stmt.where(Listing.category_id == filters.category_id)
        if filters.price_min is not None:
            stmt = stmt.where(Listing.price >= filters.price_min)
        if filters.price_max is not None:
            stmt = stmt.where(Listing.price <= filters.price_max)
        if filters.condition:
            stmt = stmt.where(Listing.condition == filters.condition)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(Listing.published_at.desc()).offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(stmt)
        ids = [row[0] for row in result.all()]

        return SearchResult(listing_ids=ids, total=total)

    async def index_listing(self, listing) -> None:
        pass  # search_vector يتحدث تلقائياً عبر trigger — لا شي لعمله هنا

    async def remove_listing(self, listing_id: UUID) -> None:
        pass  # الحذف الفعلي بـ status/deleted_at على الجدول نفسه — كافي لاستبعاده من WHERE status='active'
