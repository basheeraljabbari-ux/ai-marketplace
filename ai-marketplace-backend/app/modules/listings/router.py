import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, get_current_user, Pagination
from app.core.rate_limit import limiter, AI_GENERATE_RATE_LIMIT
from app.modules.ai.service import AIService
from app.modules.listings.models import Listing, ListingImage
from app.modules.listings.repository import ListingRepository
from app.modules.listings.schemas import (
    ListingCreate, ListingUpdate, ListingDetailOut, ListingStatusUpdate, ListingImageOut,
    AIGenerateRequest, AIGenerateJobOut, PriceInsightOut, BumpResultOut,
)
from app.modules.listings.service import ListingService
from app.modules.search.interface import SearchFilters
from app.modules.search.service import SearchService
from app.shared.utils.storage import StorageService

router = APIRouter(prefix="/listings", tags=["listings"])


def get_listing_service(db: AsyncSession = Depends(get_db)) -> ListingService:
    return ListingService(db, SearchService(db))


@router.get("")
async def search_listings(
    q: str | None = None,
    city_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    condition: str | None = None,
    pagination: Pagination = Depends(),
    db: AsyncSession = Depends(get_db),
):
    search = SearchService(db)
    filters = SearchFilters(city_id=city_id, category_id=category_id, price_min=price_min, price_max=price_max, condition=condition)
    result = await search.search(q, filters, pagination.page, pagination.limit)
    # ملاحظة: تحميل تفاصيل الكروت (عنوان/صورة/سعر) لهذي الـ IDs يكون بجلب مجمّع من listings
    # — محذوف هنا للاختصار، التنفيذ الكامل يستخدم repository.get_cards_by_ids(result.listing_ids)
    return {"listing_ids": result.listing_ids, "total": result.total, "page": pagination.page}


@router.post("", response_model=ListingDetailOut, status_code=201)
async def create_listing(
    data: ListingCreate,
    current: CurrentUser = Depends(get_current_user),
    svc: ListingService = Depends(get_listing_service),
):
    return await svc.create_draft(current.id, data)


@router.post("/ai-generate", response_model=AIGenerateJobOut, status_code=202)
@limiter.limit(AI_GENERATE_RATE_LIMIT)
async def ai_generate_listing(
    request: Request,
    data: AIGenerateRequest,
    current: CurrentUser = Depends(get_current_user),
    svc: ListingService = Depends(get_listing_service),
    ai: AIService = Depends(AIService),
):
    if data.listing_id:
        # مسار الصور الفعلية: المسودة أُنشئت وصورها رُفعت مسبقاً عبر /listings و /listings/{id}/images
        listing = await svc.get_listing_or_404(data.listing_id)
        if listing.seller_id != current.id:
            raise HTTPException(403, "Not the owner of this draft")
        draft_id = listing.id
    else:
        # مسار توافقي قديم: ننشئ مسودة فاضية (image_urls خارجية، مو مرفوعة عبر النظام)
        draft = await svc.create_draft(current.id, ListingCreate(
            title="مسودة قيد التحليل",
            condition=data.condition,
        ))
        draft_id = draft.id

    job_id = ai.enqueue_listing_generation(draft_id, data.image_urls, data.condition)
    return AIGenerateJobOut(job_id=job_id, status="queued", listing_id=draft_id)


@router.get("/ai-generate/{job_id}/status", response_model=AIGenerateJobOut)
async def get_ai_job_status(job_id: str, ai: AIService = Depends(AIService)):
    status_ = ai.get_job_status(job_id)
    if status_ == "not_found":
        raise HTTPException(404, "Job not found")

    listing_id = None
    if status_ == "finished":
        result = ai.get_job_result(job_id)
        if result and result.get("listing_id"):
            listing_id = result["listing_id"]

    return AIGenerateJobOut(job_id=job_id, status=status_, listing_id=listing_id)


@router.get("/price-insight", response_model=PriceInsightOut)
async def get_price_insight(
    category_id: uuid.UUID,
    condition: str | None = None,
    exclude_listing_id: uuid.UUID | None = None,
    svc: ListingService = Depends(get_listing_service),
):
    # لازم يكون قبل مسار /{listing_id} — وإلا FastAPI يحاول يفسّر "price-insight" كـ UUID ويفشل بـ 422
    return await svc.get_price_insight(category_id, condition, exclude_listing_id)


@router.get("/mine", response_model=list[ListingDetailOut])
async def list_my_listings(
    current: CurrentUser = Depends(get_current_user),
    pagination: Pagination = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # إعلانات المستخدم الحالي بكل الحالات (draft/active/sold/removed) مع البيانات الكاملة
    # (صور + last_bumped_at) — مخصص لصفحة "إعلاناتي". يختلف عن /users/{id}/listings
    # العام اللي يرجّع النشطة فقط بصيغة ListingCardOut المختصرة.
    # لازم يكون قبل مسار /{listing_id} وإلا "mine" يُفسَّر كـ UUID ويفشل بـ 422.
    repo = ListingRepository(db)
    listings, _ = await repo.list_by_seller(current.id, status=None, offset=pagination.offset, limit=pagination.limit)
    return listings


@router.get("/{listing_id}", response_model=ListingDetailOut)
async def get_listing(listing_id: uuid.UUID, svc: ListingService = Depends(get_listing_service)):
    listing = await svc.get_listing_or_404(listing_id)
    await svc.register_view(listing_id)
    return listing


@router.put("/{listing_id}", response_model=ListingDetailOut)
async def update_listing(
    listing_id: uuid.UUID,
    data: ListingUpdate,
    current: CurrentUser = Depends(get_current_user),
    svc: ListingService = Depends(get_listing_service),
):
    return await svc.update(listing_id, current.id, data, is_admin=(current.role == "admin"))


@router.patch("/{listing_id}/status", response_model=ListingDetailOut)
async def update_listing_status(
    listing_id: uuid.UUID,
    data: ListingStatusUpdate,
    current: CurrentUser = Depends(get_current_user),
    svc: ListingService = Depends(get_listing_service),
):
    if data.status == "active":
        return await svc.publish(listing_id, current.id)
    elif data.status == "sold":
        return await svc.mark_sold(listing_id, current.id)
    elif data.status == "removed":
        await svc.soft_delete(listing_id, current.id, is_admin=(current.role == "admin"))
        return await svc.get_listing_or_404(listing_id)
    raise HTTPException(400, "Unsupported status transition")


@router.post("/{listing_id}/bump", response_model=BumpResultOut)
async def bump_listing(
    listing_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    svc: ListingService = Depends(get_listing_service),
):
    return await svc.bump(listing_id, current.id)


@router.delete("/{listing_id}", status_code=204)
async def delete_listing(
    listing_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    svc: ListingService = Depends(get_listing_service),
):
    await svc.soft_delete(listing_id, current.id, is_admin=(current.role == "admin"))


MAX_IMAGES_PER_LISTING = 10
MAX_UPLOAD_SIZE_MB = 10


@router.post("/{listing_id}/images", response_model=ListingImageOut, status_code=201)
async def upload_listing_image(
    listing_id: uuid.UUID,
    file: UploadFile = File(...),
    current: CurrentUser = Depends(get_current_user),
    svc: ListingService = Depends(get_listing_service),
    db: AsyncSession = Depends(get_db),
):
    listing = await svc.get_listing_or_404(listing_id)
    if listing.seller_id != current.id and current.role != "admin":
        raise HTTPException(403, "Not the owner of this listing")
    if len(listing.images) >= MAX_IMAGES_PER_LISTING:
        raise HTTPException(400, f"Maximum {MAX_IMAGES_PER_LISTING} images per listing")
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "Unsupported image type")

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"Image exceeds {MAX_UPLOAD_SIZE_MB}MB limit")

    urls = StorageService().upload_listing_image(contents, file.content_type)

    image = ListingImage(
        listing_id=listing_id,
        original_url=urls["original_url"],
        thumbnail_url=urls["thumbnail_url"],
        optimized_url=urls["optimized_url"],
        width=urls["width"],
        height=urls["height"],
        sort_order=len(listing.images),
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


@router.delete("/{listing_id}/images/{image_id}", status_code=204)
async def delete_listing_image(
    listing_id: uuid.UUID,
    image_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    svc: ListingService = Depends(get_listing_service),
    db: AsyncSession = Depends(get_db),
):
    listing = await svc.get_listing_or_404(listing_id)
    if listing.seller_id != current.id and current.role != "admin":
        raise HTTPException(403, "Not the owner of this listing")

    image = await db.get(ListingImage, image_id)
    if not image or image.listing_id != listing_id:
        raise HTTPException(404, "Image not found")

    StorageService().delete_listing_images([image.original_url, image.thumbnail_url, image.optimized_url])
    await db.delete(image)
    await db.commit()
