import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parent_id: uuid.UUID | None
    name_ar: str
    name_en: str
    slug: str
    icon_url: str | None


class CategoryAttributesSchema(BaseModel):
    """يُستخدم من الـ Frontend لبناء فورم إنشاء الإعلان تلقائياً حسب الفئة."""
    category_id: uuid.UUID
    fields: list[dict[str, Any]]
