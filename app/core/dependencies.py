from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.modules.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class CurrentUser:
    """Lightweight identity extracted from the JWT — avoids a DB hit on every request
    unless the full user row is actually needed."""

    def __init__(self, id: UUID, role: str):
        self.id = id
        self.role = role


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> CurrentUser:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return CurrentUser(id=UUID(payload["sub"]), role=payload.get("role", "user"))


async def get_current_user_full(
    current: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Use only when the endpoint actually needs full user fields (email, rating, etc)."""
    user = await db.get(User, current.id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    if user.is_banned:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account banned")
    return user


def require_admin(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return current


class Pagination:
    def __init__(self, page: int = 1, limit: int = 20):
        self.page = max(page, 1)
        self.limit = min(max(limit, 1), 100)  # حماية من طلب صفحات ضخمة

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit
