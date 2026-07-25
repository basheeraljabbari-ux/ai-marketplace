import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserPublic(BaseModel):
    """ما يشوفه أي زائر عن مستخدم ثاني — لا إيميل ولا بيانات حساسة."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    avatar_url: str | None
    city_id: uuid.UUID | None
    rating_avg: float
    rating_count: int
    # بائع موثوق: 3 مبيعات مكتملة فأكثر، مع تقييم ≥ 4.0 (أو ما عنده تقييمات بعد).
    # محسوب في الـ router — مو عمود بالجدول.
    is_verified_seller: bool = False
    created_at: datetime


class UserMe(UserPublic):
    """بيانات المستخدم الكاملة — تُرجع فقط لصاحب الحساب."""
    email: EmailStr
    phone: str | None
    is_verified: bool
    preferred_language: str
    role: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    city_id: uuid.UUID | None = None
    preferred_language: str | None = None
