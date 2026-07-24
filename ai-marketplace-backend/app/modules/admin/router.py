import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_admin, Pagination
from app.modules.admin.schemas import AdminStatsOut, AdminUserOut, BanUserRequest, AuditLogOut, CategoryCreate
from app.modules.admin.service import AdminService
from app.modules.categories.schemas import CategoryOut
from app.modules.listings.schemas import ListingDetailOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def get_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)


@router.get("/stats", response_model=AdminStatsOut)
async def get_stats(svc: AdminService = Depends(get_service)):
    return await svc.get_stats()


@router.get("/users", response_model=list[AdminUserOut])
async def list_users(pagination: Pagination = Depends(), svc: AdminService = Depends(get_service)):
    return await svc.list_users(pagination.offset, pagination.limit)


@router.patch("/users/{user_id}/ban", response_model=AdminUserOut)
async def ban_user(
    user_id: uuid.UUID,
    data: BanUserRequest,
    current: CurrentUser = Depends(require_admin),
    svc: AdminService = Depends(get_service),
):
    return await svc.set_user_ban(current.id, user_id, data.is_banned, data.reason)


@router.get("/listings", response_model=list[ListingDetailOut])
async def list_all_listings(
    status: str | None = None,
    pagination: Pagination = Depends(),
    svc: AdminService = Depends(get_service),
):
    return await svc.list_listings(pagination.offset, pagination.limit, status)


@router.delete("/listings/{listing_id}", status_code=204)
async def remove_listing(
    listing_id: uuid.UUID,
    reason: str | None = None,
    current: CurrentUser = Depends(require_admin),
    svc: AdminService = Depends(get_service),
):
    await svc.remove_listing(current.id, listing_id, reason)


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def create_category(data: CategoryCreate, svc: AdminService = Depends(get_service)):
    return await svc.create_category(data.model_dump())


@router.get("/audit-logs", response_model=list[AuditLogOut])
async def get_audit_logs(pagination: Pagination = Depends(), svc: AdminService = Depends(get_service)):
    return await svc.get_audit_logs(pagination.offset, pagination.limit)
