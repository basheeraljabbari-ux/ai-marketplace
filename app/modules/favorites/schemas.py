import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    listing_id: uuid.UUID
    created_at: datetime
