import uuid
from datetime import datetime

from sqlalchemy import String, Text, Numeric, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # nullable لأن مسودات AI تُنشأ قبل تحديد الفئة (تُحدَّد بعد التحليل أو يدوياً بالمراجعة)
    category_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    city_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id"))

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="AUD")
    condition: Mapped[str | None] = mapped_column(String(30))  # new|used_like_new|used_good|used_fair
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft|active|sold|expired|removed

    # قيم ديناميكية حسب category.attributes_schema
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)

    # يُحدَّث تلقائياً بـ DB trigger (راجع alembic migration) — لا يُكتب من التطبيق مباشرة
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # آخر مرة رفع فيها البائع الإعلان مجاناً لأعلى النتائج — يفرض فترة تهدئة 48 ساعة.
    # null = ما رُفع أبداً بعد (يحق رفعه فوراً).
    last_bumped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    images: Mapped[list["ListingImage"]] = relationship(
        back_populates="listing", cascade="all, delete-orphan", order_by="ListingImage.sort_order"
    )
    ai_metadata: Mapped["ListingAIMetadata"] = relationship(
        back_populates="listing", uselist=False, cascade="all, delete-orphan"
    )


class ListingImage(Base):
    __tablename__ = "listing_images"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False)

    original_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    optimized_url: Mapped[str | None] = mapped_column(String(500))

    is_enhanced: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    listing: Mapped["Listing"] = relationship(back_populates="images")


class ListingAIMetadata(Base):
    """سجل تدقيق لما استخرجه الـ AI — منفصل عن listings.attributes النهائية
    (اللي ممكن المستخدم يعدلها) عشان نحتفظ بمخرجات النموذج الأصلية للمراجعة/التحسين لاحقاً."""
    __tablename__ = "listing_ai_metadata"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("listings.id"), unique=True, nullable=False)

    detected_brand: Mapped[str | None] = mapped_column(String(100))
    detected_color: Mapped[str | None] = mapped_column(String(50))
    suggested_price_min: Mapped[float | None] = mapped_column(Numeric(12, 2))
    suggested_price_max: Mapped[float | None] = mapped_column(Numeric(12, 2))
    ai_confidence: Mapped[float | None] = mapped_column(Numeric(3, 2))
    raw_ai_response: Mapped[dict | None] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    listing: Mapped["Listing"] = relationship(back_populates="ai_metadata")
