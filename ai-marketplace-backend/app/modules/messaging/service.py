import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.listings.models import Listing
from app.modules.messaging.models import Conversation, Message
from app.modules.messaging.schemas import MessageCreate, ConversationOut


class MessagingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_conversation(self, listing_id: uuid.UUID, buyer_id: uuid.UUID) -> Conversation:
        listing = await self.db.get(Listing, listing_id)
        if not listing:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Listing not found")
        if listing.seller_id == buyer_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot message yourself about your own listing")

        stmt = select(Conversation).where(
            Conversation.listing_id == listing_id,
            Conversation.buyer_id == buyer_id,
            Conversation.seller_id == listing.seller_id,
        )
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if existing:
            return existing

        conversation = Conversation(listing_id=listing_id, buyer_id=buyer_id, seller_id=listing.seller_id)
        self.db.add(conversation)
        await self.db.flush()
        await self.db.commit()
        return conversation

    async def list_conversations(self, user_id: uuid.UUID) -> list[ConversationOut]:
        stmt = select(Conversation).where(
            (Conversation.buyer_id == user_id) | (Conversation.seller_id == user_id)
        ).order_by(Conversation.last_message_at.desc().nullslast())
        result = await self.db.execute(stmt)
        conversations = result.scalars().all()

        out = []
        for c in conversations:
            unread = c.buyer_unread_count if c.buyer_id == user_id else c.seller_unread_count
            out.append(ConversationOut(
                id=c.id, listing_id=c.listing_id, buyer_id=c.buyer_id, seller_id=c.seller_id,
                last_message_preview=c.last_message_preview, last_message_at=c.last_message_at,
                last_message_sender_id=c.last_message_sender_id, unread_count=unread, created_at=c.created_at,
            ))
        return out

    async def get_conversation_or_404(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Conversation:
        conv = await self.db.get(Conversation, conversation_id)
        if not conv or user_id not in (conv.buyer_id, conv.seller_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
        return conv

    async def send_message(self, conversation_id: uuid.UUID, sender_id: uuid.UUID, data: MessageCreate) -> Message:
        conv = await self.get_conversation_or_404(conversation_id, sender_id)

        message = Message(
            conversation_id=conversation_id, sender_id=sender_id,
            message_type=data.message_type, content=data.content, attachments=data.attachments,
        )
        self.db.add(message)

        # تحديث الحقول denormalized ضمن نفس الـ transaction — يمنع data drift
        preview = (data.content or "📎 مرفق")[:200]
        now = datetime.now(timezone.utc)
        conv.last_message_preview = preview
        conv.last_message_at = now
        conv.last_message_sender_id = sender_id

        if sender_id == conv.buyer_id:
            conv.seller_unread_count += 1
        else:
            conv.buyer_unread_count += 1

        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def list_messages(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> list[Message]:
        await self.get_conversation_or_404(conversation_id, user_id)
        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_read(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> None:
        conv = await self.get_conversation_or_404(conversation_id, user_id)

        await self.db.execute(
            update(Message).where(Message.conversation_id == conversation_id, Message.sender_id != user_id)
            .values(is_read=True)
        )
        if user_id == conv.buyer_id:
            conv.buyer_unread_count = 0
        else:
            conv.seller_unread_count = 0
        await self.db.commit()
