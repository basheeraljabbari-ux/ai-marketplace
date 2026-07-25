from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.geo.models import City
from app.modules.geo.schemas import CityOut

router = APIRouter(prefix="/cities", tags=["geo"])


@router.get("", response_model=list[CityOut])
async def list_cities(db: AsyncSession = Depends(get_db)):
    """قائمة المدن الفعّالة — يستخدمها الفرونت لقوائم اختيار المدينة (الملف الشخصي، الإعلانات)."""
    stmt = select(City).where(City.is_active.is_(True)).order_by(City.name_en)
    result = await db.execute(stmt)
    return result.scalars().all()
