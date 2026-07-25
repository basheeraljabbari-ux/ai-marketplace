import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, get_current_user, get_current_user_full, Pagination
from app.modules.listings.repository import ListingRepository
from app.modules.listings.schemas import ListingCardOut
from app.modules.users.models import User
from app.modules.users.schemas import UserMe, UserPublic, UserUpdate
from app.shared.utils.storage import StorageService

router = APIRouter(prefix="/users", tags=["users"])

AVATAR_MAX_SIZE_MB = 5


@router.get("/me", response_model=UserMe)
async def get_me(user: User = Depends(get_current_user_full)):
    return user


@router.put("/me", response_model=UserMe)
async def update_me(data: UserUpdate, user: User = Depends(get_current_user_full), db: AsyncSession = Depends(get_db)):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/me/avatar", response_model=UserMe)
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "Unsupported image type — use JPEG, PNG or WebP")

    contents = await file.read()
    if len(contents) > AVATAR_MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"Image exceeds {AVATAR_MAX_SIZE_MB}MB limit")

    user.avatar_url = StorageService().upload_avatar(contents, file.content_type)
    await db.commit()
    await db.refresh(user)
    return user


VERIFIED_SELLER_MIN_SALES = 3
VERIFIED_SELLER_MIN_RATING = 4.0


@router.get("/{user_id}", response_model=UserPublic)
async def get_public_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(404, "User not found")

    # بائع موثوق: 3 مبيعات مكتملة فأكثر، وتقييم ≥ 4.0 — أو ما عنده أي تقييمات بعد
    # (ما نعاقب البائع الجديد النشط بغياب التقييمات).
    sold_count = await ListingRepository(db).count_sold_by_seller(user_id)
    is_verified_seller = sold_count >= VERIFIED_SELLER_MIN_SALES and (
        user.rating_count == 0 or float(user.rating_avg) >= VERIFIED_SELLER_MIN_RATING
    )

    return UserPublic.model_validate(user).model_copy(update={"is_verified_seller": is_verified_seller})


@router.get("/{user_id}/listings", response_model=list[ListingCardOut])
async def get_user_listings(
    user_id: uuid.UUID,
    pagination: Pagination = Depends(),
    db: AsyncSession = Depends(get_db),
):
    repo = ListingRepository(db)
    listings, _ = await repo.list_by_seller(user_id, status="active", offset=pagination.offset, limit=pagination.limit)
    return listings
