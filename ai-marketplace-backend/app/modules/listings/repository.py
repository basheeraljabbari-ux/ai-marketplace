import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.listings.models import Listing, ListingImage


class ListingRepository:
    """طبقة وصول DB خام — بدون أي منطق عمل. الـ Service هو اللي يقرر متى/كيف تُستخدم.

    كل عملية كتابة تعمل commit صراحةً: get_db ما يعمل commit، والـ session
    يسوي rollback تلقائياً وقت الإغلاق — فبدون commit كانت كل كتابات الإعلانات
    تضيع بصمت رغم إن الـ response يرجع نجاح. نفس أسلوب باقي الموديولات
    (auth/favorites/messaging/admin كلها تعمل commit صراحةً).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, listing_id: uuid.UUID, include_images: bool = True) -> Listing | None:
        stmt = select(Listing).where(Listing.id == listing_id, Listing.deleted_at.is_(None))
        if include_images:
            stmt = stmt.options(selectinload(Listing.images))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_seller(self, seller_id: uuid.UUID, status: str | None, offset: int, limit: int) -> tuple[list[Listing], int]:
        stmt = select(Listing).where(Listing.seller_id == seller_id, Listing.deleted_at.is_(None))
        if status:
            stmt = stmt.where(Listing.status == status)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(Listing.created_at.desc()).offset(offset).limit(limit).options(selectinload(Listing.images))
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, listing: Listing) -> Listing:
        self.db.add(listing)
        await self.db.flush()
        await self.db.commit()
        return listing

    async def save(self, listing: Listing) -> Listing:
        await self.db.flush()
        await self.db.commit()
        return listing

    async def increment_view_count(self, listing_id: uuid.UUID) -> None:
        # UPDATE مباشر بدون تحميل الكائن كامل — أخف على DB لعملية متكررة جداً
        stmt = (
            Listing.__table__.update()
            .where(Listing.id == listing_id)
            .values(view_count=Listing.view_count + 1)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def add_images(self, listing_id: uuid.UUID, images: list[ListingImage]) -> None:
        for img in images:
            img.listing_id = listing_id
            self.db.add(img)
        await self.db.flush()
        await self.db.commit()
