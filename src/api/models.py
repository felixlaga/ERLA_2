"""Pydantic models for the ERLA product API skeleton."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Allowed research session statuses."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BranchStatus(str, Enum):
    """Allowed branch statuses."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    PRUNED = "pruned"
    FAILED = "failed"


class BranchMode(str, Enum):
    """Allowed branch modes."""

    SEARCH_SUMMARIZE = "search_summarize"
    HYPOTHESIS = "hypothesis"
    SYNTHESIS = "synthesis"
    GAP_ANALYSIS = "gap_analysis"


class ProjectCreate(BaseModel):
    """Payload for creating a project."""

    title: str
    description: str | None = None
    field: str | None = None
    settings: dict[str, Any] = Field(default_factory=dict)


class Project(ProjectCreate):
    """A long-lived research workspace."""

    id: str
    created_at: datetime
    updated_at: datetime


class SessionCreate(BaseModel):
    """Payload for creating a research session."""

    project_id: str | None = None
    initial_query: str
    source_providers: list[str] = Field(default_factory=lambda: ["semantic_scholar"])
    filters: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)


class ResearchSession(SessionCreate):
    """A product-level research session."""

    id: str
    status: SessionStatus = SessionStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class BranchCreate(BaseModel):
    """Payload for creating a branch in the API skeleton."""

    query: str
    label: str | None = None
    rationale: str | None = None
    mode: BranchMode = BranchMode.SEARCH_SUMMARIZE


class BranchPatch(BaseModel):
    """Payload for updating branch metadata or status."""

    query: str | None = None
    label: str | None = None
    rationale: str | None = None
    status: BranchStatus | None = None


class Branch(BranchCreate):
    """A Scout branch exploring part of a research session."""

    id: str
    session_id: str
    parent_branch_id: str | None = None
    status: BranchStatus = BranchStatus.PENDING
    depth: int = 0
    context_tokens_used: int = 0
    max_context_tokens: int | None = None
    created_at: datetime
    updated_at: datetime


class BranchSplitRequest(BaseModel):
    """Payload for splitting a branch into child branches."""

    branches: list[BranchCreate]


class Paper(BaseModel):
    """Normalized paper metadata exposed by the product API."""

    id: str
    session_id: str
    branch_id: str | None = None
    paper_id: str
    title: str
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    citation_count: int | None = None
    created_at: datetime


class Event(BaseModel):
    """Realtime and historical event log entry."""

    id: str
    session_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    branch_id: str | None = None
    paper_id: str | None = None
    severity: str = "info"
    created_at: datetime


class RuntimeLoopBinding(BaseModel):
    """Binding between a product session and runtime research-loop state."""

    session_id: str
    loop_id: str
    loop_number: int
    root_branch_id: str
    created_at: datetime
    updated_at: datetime


class SessionSnapshot(BaseModel):
    """A reconstructable session view for dashboard clients."""

    session: ResearchSession
    runtime_loop: RuntimeLoopBinding | None = None
    branches: list[Branch] = Field(default_factory=list)
    papers: list[Paper] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
