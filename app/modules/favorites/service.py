import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.favorites.models import Favorite


class FavoritesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> Favorite:
        existing = await self._get(user_id, listing_id)
        if existing:
            return existing  # idempotent — الضغط مرتين على القلب ما يرمي خطأ

        fav = Favorite(user_id=user_id, listing_id=listing_id)
        self.db.add(fav)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Listing not found")
        return fav

    async def remove(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> None:
        fav = await self._get(user_id, listing_id)
        if fav:
            await self.db.delete(fav)
            await self.db.commit()

    async def list_for_user(self, user_id: uuid.UUID) -> list[Favorite]:
        stmt = select(Favorite).where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> Favorite | None:
        stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.listing_id == listing_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()
