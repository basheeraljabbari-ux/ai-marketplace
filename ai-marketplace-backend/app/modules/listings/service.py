import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.listings.models import Listing
from app.modules.listings.repository import ListingRepository
from app.modules.listings.schemas import ListingCreate, ListingUpdate
from app.modules.listings.validators import validate_attributes_against_schema
from app.modules.search.service import SearchService

LISTING_EXPIRY_DAYS = 60


class ListingService:
    """كل منطق العمل الخاص بالإعلانات. الـ router ينادي هذا الكلاس فقط —
    لا يلمس Repository أو Models مباشرة."""

    def __init__(self, db: AsyncSession, search_service: SearchService | None = None):
        self.db = db
        self.repo = ListingRepository(db)
        self.search = search_service or SearchService()

    async def get_listing_or_404(self, listing_id: uuid.UUID) -> Listing:
        listing = await self.repo.get_by_id(listing_id)
        if not listing:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Listing not found")
        return listing

    async def create_draft(self, seller_id: uuid.UUID, data: ListingCreate) -> Listing:
        listing = Listing(
            seller_id=seller_id,
            category_id=data.category_id,
            city_id=data.city_id,
            title=data.title,
            description=data.description,
            price=data.price,
            condition=data.condition,
            attributes=data.attributes,
            status="draft",
        )
        await self.repo.create(listing)
        return listing

    async def update(self, listing_id: uuid.UUID, seller_id: uuid.UUID, data: ListingUpdate, is_admin: bool = False) -> Listing:
        listing = await self.get_listing_or_404(listing_id)
        self._assert_owner_or_admin(listing, seller_id, is_admin)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(listing, field, value)

        await self.repo.save(listing)
        if listing.status == "active":
            await self.search.index_listing(listing)
        return listing

    async def publish(self, listing_id: uuid.UUID, seller_id: uuid.UUID) -> Listing:
        listing = await self.get_listing_or_404(listing_id)
        self._assert_owner_or_admin(listing, seller_id, is_admin=False)

        if not listing.title or listing.price is None or listing.category_id is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Listing incomplete — title, price and category required")

        from app.modules.categories.models import Category
        category = await self.db.get(Category, listing.category_id)
        if category:
            validate_attributes_against_schema(category, listing.attributes)

        now = datetime.now(timezone.utc)
        listing.status = "active"
        listing.published_at = now
        listing.expires_at = now.replace(day=now.day) + __import__("datetime").timedelta(days=LISTING_EXPIRY_DAYS)

        await self.repo.save(listing)
        await self.search.index_listing(listing)
        return listing

    async def mark_sold(self, listing_id: uuid.UUID, seller_id: uuid.UUID) -> Listing:
        listing = await self.get_listing_or_404(listing_id)
        self._assert_owner_or_admin(listing, seller_id, is_admin=False)

        listing.status = "sold"
        listing.sold_at = datetime.now(timezone.utc)
        await self.repo.save(listing)
        await self.search.remove_listing(listing.id)  # مباع = يختفي من البحث فوراً
        return listing

    async def soft_delete(self, listing_id: uuid.UUID, seller_id: uuid.UUID, is_admin: bool = False) -> None:
        listing = await self.get_listing_or_404(listing_id)
        self._assert_owner_or_admin(listing, seller_id, is_admin)

        # حذف الصور فعلياً من S3 قبل حذف السجلات — يمنع تسريب bucket storage بمرور الوقت
        if listing.images:
            from app.shared.utils.storage import StorageService
            urls = [u for img in listing.images for u in (img.original_url, img.thumbnail_url, img.optimized_url)]
            StorageService().delete_listing_images(urls)

        listing.deleted_at = datetime.now(timezone.utc)
        listing.status = "removed"
        await self.repo.save(listing)
        await self.search.remove_listing(listing.id)

    async def register_view(self, listing_id: uuid.UUID) -> None:
        await self.repo.increment_view_count(listing_id)

    def _assert_owner_or_admin(self, listing: Listing, user_id: uuid.UUID, is_admin: bool) -> None:
        if listing.seller_id != user_id and not is_admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the owner of this listing")
