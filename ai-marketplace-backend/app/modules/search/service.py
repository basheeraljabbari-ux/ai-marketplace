from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.search.interface import SearchProvider

settings = get_settings()


class SearchService:
    """الغلاف الوحيد اللي باقي الموديولات تتعامل معه. يقرر أي Provider يشتغل
    حسب settings.SEARCH_PROVIDER — التبديل لـ OpenSearch = تغيير هذا الملف فقط."""

    def __init__(self, db: AsyncSession | None = None):
        self._provider: SearchProvider | None = None
        self._db = db

    def _get_provider(self) -> SearchProvider:
        if self._provider is None:
            if settings.SEARCH_PROVIDER == "postgres":
                from app.modules.search.postgres_provider import PostgresSearchProvider
                self._provider = PostgresSearchProvider(self._db)
            elif settings.SEARCH_PROVIDER == "opensearch":
                # from app.modules.search.opensearch_provider import OpenSearchProvider
                # self._provider = OpenSearchProvider(...)
                raise NotImplementedError("OpenSearch provider not implemented yet — planned for a later phase")
            else:
                raise ValueError(f"Unknown SEARCH_PROVIDER: {settings.SEARCH_PROVIDER}")
        return self._provider

    async def search(self, query, filters, page, limit):
        return await self._get_provider().search(query, filters, page, limit)

    async def index_listing(self, listing) -> None:
        await self._get_provider().index_listing(listing)

    async def remove_listing(self, listing_id) -> None:
        await self._get_provider().remove_listing(listing_id)
