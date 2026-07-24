import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ListingImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    thumbnail_url: str | None
    optimized_url: str | None
    original_url: str
    sort_order: int


class ListingCreate(BaseModel):
    """المسار اليدوي — المستخدم يعبي كل شي بنفسه.
    category_id اختياري لأن AIService ينشئ draft أولي بدون فئة محددة؛
    publish() يتحقق من وجودها إجبارياً قبل النشر الفعلي."""
    category_id: uuid.UUID | None = None
    city_id: uuid.UUID | None = None
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    condition: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class ListingUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    city_id: uuid.UUID | None = None
    title: str | None = None
    description: str | None = None
    price: float | None = None
    condition: str | None = None
    attributes: dict[str, Any] | None = None


class ListingStatusUpdate(BaseModel):
    status: str  # active|sold|removed (draft/expired تُدار من السيرفر فقط)


class ListingCardOut(BaseModel):
    """نسخة مختصرة — تُستخدم بنتائج البحث وقوائم الكروت (بدون description الكامل)."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    price: float | None
    currency: str
    city_id: uuid.UUID | None
    status: str
    cover_image: str | None = None  # thumbnail_url لأول صورة
    created_at: datetime


class ListingDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    seller_id: uuid.UUID
    # اختياري لأن المسودة الجديدة تُنشأ بلا فئة (نفس سبب ListingCreate.category_id)؛
    # إجباريته هنا كانت تسبب 500 عند إرجاع أي draft بلا فئة.
    category_id: uuid.UUID | None
    city_id: uuid.UUID | None
    title: str
    description: str | None
    price: float | None
    currency: str
    condition: str | None
    status: str
    attributes: dict[str, Any]
    view_count: int
    is_ai_generated: bool
    images: list[ListingImageOut]
    published_at: datetime | None
    created_at: datetime


class AIGenerateRequest(BaseModel):
    listing_id: uuid.UUID | None = None  # لو موجود: نستخدم مسودة موجودة (صور مرفوعة فعلياً)؛ لو فاضي: ننشئ مسودة جديدة
    image_urls: list[str] = Field(min_length=1, max_length=10)
    condition: str


class AIGenerateJobOut(BaseModel):
    job_id: str
    status: str  # queued|processing|done|failed
    listing_id: uuid.UUID | None = None


class AIGenerateResultOut(BaseModel):
    job_id: str
    status: str
    draft_listing: ListingDetailOut | None = None
    error: str | None = None
