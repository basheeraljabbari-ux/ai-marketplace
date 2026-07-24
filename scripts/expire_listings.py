"""
يُشغَّل دورياً (يومياً) عبر cron خارجي أو RQ Scheduler:
    0 3 * * *  cd /path/to/project && python -m scripts.expire_listings

يحول كل إعلان status='active' انتهى expires_at إلى status='expired'.
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import update

from app.core.database import AsyncSessionLocal
from app.modules.listings.models import Listing


async def expire_listings():
    async with AsyncSessionLocal() as db:
        stmt = (
            update(Listing)
            .where(Listing.status == "active", Listing.expires_at <= datetime.now(timezone.utc))
            .values(status="expired")
        )
        result = await db.execute(stmt)
        await db.commit()
        print(f"Expired {result.rowcount} listing(s).")


if __name__ == "__main__":
    asyncio.run(expire_listings())
