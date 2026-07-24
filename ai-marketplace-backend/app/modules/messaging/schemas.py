import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    listing_id: uuid.UUID


class MessageCreate(BaseModel):
    content: str | None = Field(default=None, max_length=2000)
    message_type: str = "text"  # text|image (system/ai تُنشأ من السيرفر فقط، مو من المستخدم)
    attachments: list[dict[str, Any]] | None = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID | None
    message_type: str
    content: str | None
    attachments: list[dict[str, Any]] | None
    is_read: bool
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    listing_id: uuid.UUID
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    last_message_preview: str | None
    last_message_at: datetime | None
    last_message_sender_id: uuid.UUID | None
    unread_count: int  # يُحسب حسب مين يشوف (buyer_unread_count أو seller_unread_count)
    created_at: datetime
