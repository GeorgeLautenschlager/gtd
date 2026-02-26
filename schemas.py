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
    clarified_result_type: str | None = None

    class Config:
        orm_mode = True


# NextAction Schemas
class NextActionCreate(BaseModel):
    project_id: int | None = None
    description: str
    context: str
    energy_required: str
    time_estimate: int | None = None


class NextActionResponse(BaseModel):
    id: int
    project_id: int | None = None
    description: str
    context: str
    energy_required: str
    time_estimate: int | None = None
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        orm_mode = True


# Project Schemas
class ProjectCreate(BaseModel):
    name: str
    outcome_description: str
    status: str = "active"


class ProjectResponse(BaseModel):
    id: int
    name: str
    outcome_description: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    next_actions: list[NextActionResponse] = []

    class Config:
        orm_mode = True


# Clarification Request
class ClarifyRequest(BaseModel):
    inbox_item_id: int
    action: str  # next_action, project, trash, reference, someday
    project_data: ProjectCreate | None = None
    next_action_data: NextActionCreate | None = None
