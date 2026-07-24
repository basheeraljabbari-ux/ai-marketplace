from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.modules.listings.models import Listing


@dataclass
class SearchFilters:
    city_id: UUID | None = None
    category_id: UUID | None = None
    price_min: float | None = None
    price_max: float | None = None
    condition: str | None = None


@dataclass
class SearchResult:
    listing_ids: list[UUID]
    total: int


class SearchProvider(ABC):
    """أي مزوّد بحث (PostgreSQL FTS اليوم، OpenSearch لاحقاً) لازم يطبّق هذا العقد.
    لا شي خارج /modules/search يعرف أي تنفيذ فعلي مستخدم."""

    @abstractmethod
    async def search(self, query: str | None, filters: SearchFilters, page: int, limit: int) -> SearchResult: ...

    @abstractmethod
    async def index_listing(self, listing: Listing) -> None: ...

    @abstractmethod
    async def remove_listing(self, listing_id: UUID) -> None: ...
