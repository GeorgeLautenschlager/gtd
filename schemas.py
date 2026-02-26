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


# Dashboard / Smart filtering models
class ContextFilter(BaseModel):
    context: str | None = None
    time_available: int | None = None
    energy_level: str | None = None
    has_project: bool | None = None


class DashboardStats(BaseModel):
    total_active_actions: int
    by_context: dict[str, int]
    by_energy: dict[str, int]
    stale_actions: int
    inbox_count: int
    active_projects: int


class ActionWithProject(NextActionResponse):
    project_name: str | None = None
    project_outcome: str | None = None

    class Config:
        orm_mode = True
