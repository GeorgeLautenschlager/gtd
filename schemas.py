from __future__ import annotations
from datetime import datetime

from pydantic import BaseModel, Field


class InboxItemCreate(BaseModel):
    content: str = Field(..., min_length=1)


class InboxItemResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    processed: bool
    processed_at: datetime | None

    class Config:
        orm_mode = True
