from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter, AUTH_RATE_LIMIT
from app.modules.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit(AUTH_RATE_LIMIT)
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).register(data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(data.email, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).refresh(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout():
    # الـ MVP يعتمد على انتهاء صلاحية الـ access token القصيرة (15 دقيقة).
    # لو احتجنا invalidation فوري لاحقاً، نضيف جدول/Redis set لـ blacklisted refresh tokens هنا فقط.
    return None
