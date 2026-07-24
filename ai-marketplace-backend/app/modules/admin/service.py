import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.models import AuditLog
from app.modules.categories.models import Category
from app.modules.listings.models import Listing
from app.modules.users.models import User


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self) -> dict[str, Any]:
        total_users = (await self.db.execute(select(func.count()).select_from(User))).scalar_one()
        total_listings = (await self.db.execute(select(func.count()).select_from(Listing).where(Listing.deleted_at.is_(None)))).scalar_one()
        active_listings = (await self.db.execute(select(func.count()).select_from(Listing).where(Listing.status == "active"))).scalar_one()

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        listings_today = (await self.db.execute(
            select(func.count()).select_from(Listing).where(Listing.created_at >= today_start)
        )).scalar_one()

        top_categories_stmt = (
            select(Category.name_ar, func.count(Listing.id).label("count"))
            .join(Listing, Listing.category_id == Category.id)
            .where(Listing.status == "active")
            .group_by(Category.name_ar)
            .order_by(func.count(Listing.id).desc())
            .limit(5)
        )
        top_categories = [{"name": row[0], "count": row[1]} for row in (await self.db.execute(top_categories_stmt)).all()]

        return {
            "total_users": total_users,
            "total_listings": total_listings,
            "active_listings": active_listings,
            "listings_today": listings_today,
            "top_categories": top_categories,
        }

    async def list_users(self, offset: int, limit: int) -> list[User]:
        stmt = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def list_listings(self, offset: int, limit: int, status_filter: str | None = None) -> list[Listing]:
        stmt = select(Listing).where(Listing.deleted_at.is_(None))
        if status_filter:
            stmt = stmt.where(Listing.status == status_filter)
        stmt = stmt.order_by(Listing.created_at.desc()).offset(offset).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def set_user_ban(self, admin_id: uuid.UUID, user_id: uuid.UUID, is_banned: bool, reason: str | None) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        user.is_banned = is_banned
        await self._log_action(admin_id, "ban_user" if is_banned else "unban_user", "user", user_id, {"reason": reason})
        await self.db.commit()
        return user

    async def remove_listing(self, admin_id: uuid.UUID, listing_id: uuid.UUID, reason: str | None) -> None:
        listing = await self.db.get(Listing, listing_id)
        if not listing:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Listing not found")

        listing.status = "removed"
        listing.deleted_at = datetime.now(timezone.utc)
        await self._log_action(admin_id, "remove_listing", "listing", listing_id, {"reason": reason})
        await self.db.commit()

    async def create_category(self, data: dict) -> Category:
        category = Category(**data)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def get_audit_logs(self, offset: int, limit: int) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def _log_action(self, admin_id: uuid.UUID, action: str, target_type: str, target_id: uuid.UUID, metadata: dict) -> None:
        self.db.add(AuditLog(admin_id=admin_id, action=action, target_type=target_type, target_id=target_id, log_metadata=metadata))
