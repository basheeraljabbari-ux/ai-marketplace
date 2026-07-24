import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AdminStatsOut(BaseModel):
    total_users: int
    total_listings: int
    active_listings: int
    listings_today: int
    top_categories: list[dict[str, Any]]


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_banned: bool
    is_verified: bool
    created_at: datetime


class BanUserRequest(BaseModel):
    is_banned: bool
    reason: str | None = None


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    admin_id: uuid.UUID
    action: str
    target_type: str
    target_id: uuid.UUID
    created_at: datetime


class CategoryCreate(BaseModel):
    parent_id: uuid.UUID | None = None
    name_ar: str
    name_en: str
    slug: str
    icon_url: str | None = None
    attributes_schema: dict[str, Any] = {"fields": []}
