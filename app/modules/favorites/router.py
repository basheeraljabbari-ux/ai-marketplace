import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, get_current_user
from app.modules.favorites.schemas import FavoriteOut
from app.modules.favorites.service import FavoritesService

router = APIRouter(prefix="/favorites", tags=["favorites"])


def get_service(db: AsyncSession = Depends(get_db)) -> FavoritesService:
    return FavoritesService(db)


@router.get("", response_model=list[FavoriteOut])
async def list_favorites(current: CurrentUser = Depends(get_current_user), svc: FavoritesService = Depends(get_service)):
    return await svc.list_for_user(current.id)


@router.post("/{listing_id}", response_model=FavoriteOut, status_code=201)
async def add_favorite(listing_id: uuid.UUID, current: CurrentUser = Depends(get_current_user), svc: FavoritesService = Depends(get_service)):
    return await svc.add(current.id, listing_id)


@router.delete("/{listing_id}", status_code=204)
async def remove_favorite(listing_id: uuid.UUID, current: CurrentUser = Depends(get_current_user), svc: FavoritesService = Depends(get_service)):
    await svc.remove(current.id, listing_id)
