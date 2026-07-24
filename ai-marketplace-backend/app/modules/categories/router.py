from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.categories.models import Category
from app.modules.categories.schemas import CategoryOut, CategoryAttributesSchema

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
async def list_categories(parent_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    """بدون parent_id: يرجع الفئات الجذرية. مع parent_id: يرجع الفئات الفرعية."""
    stmt = select(Category).where(Category.parent_id == parent_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{category_id}/attributes-schema", response_model=CategoryAttributesSchema)
async def get_attributes_schema(category_id: UUID, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    return CategoryAttributesSchema(
        category_id=category.id,
        fields=category.attributes_schema.get("fields", []),
    )
