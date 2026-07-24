import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, get_current_user
from app.modules.messaging.schemas import ConversationCreate, ConversationOut, MessageCreate, MessageOut
from app.modules.messaging.service import MessagingService

router = APIRouter(prefix="/conversations", tags=["messaging"])


def get_service(db: AsyncSession = Depends(get_db)) -> MessagingService:
    return MessagingService(db)


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    current: CurrentUser = Depends(get_current_user),
    svc: MessagingService = Depends(get_service),
):
    return await svc.list_conversations(current.id)


@router.post("", response_model=ConversationOut, status_code=201)
async def start_conversation(
    data: ConversationCreate,
    current: CurrentUser = Depends(get_current_user),
    svc: MessagingService = Depends(get_service),
):
    conv = await svc.get_or_create_conversation(data.listing_id, current.id)
    unread = conv.buyer_unread_count if conv.buyer_id == current.id else conv.seller_unread_count
    return ConversationOut(
        id=conv.id, listing_id=conv.listing_id, buyer_id=conv.buyer_id, seller_id=conv.seller_id,
        last_message_preview=conv.last_message_preview, last_message_at=conv.last_message_at,
        last_message_sender_id=conv.last_message_sender_id, unread_count=unread, created_at=conv.created_at,
    )


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conversation_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    svc: MessagingService = Depends(get_service),
):
    messages = await svc.list_messages(conversation_id, current.id)
    await svc.mark_read(conversation_id, current.id)
    return messages


@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
    conversation_id: uuid.UUID,
    data: MessageCreate,
    current: CurrentUser = Depends(get_current_user),
    svc: MessagingService = Depends(get_service),
):
    return await svc.send_message(conversation_id, current.id, data)
