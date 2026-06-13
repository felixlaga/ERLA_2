"""Routes for the ERLA product API skeleton."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from .models import (
    Branch,
    BranchPatch,
    BranchSplitRequest,
    Event,
    Paper,
    Project,
    ProjectCreate,
    ResearchSession,
    RuntimeLoopBinding,
    SessionCreate,
    SessionSnapshot,
    SessionStatus,
)
from .repository import ConflictError, InMemoryRepository, NotFoundError, RepositoryError

router = APIRouter()


def get_repository(request: Request) -> InMemoryRepository:
    """Get the repository attached to the FastAPI app."""

    return request.app.state.repository


def handle_repository_error(exc: RepositoryError) -> None:
    """Translate repository errors into HTTP errors."""

    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""

    return {"status": "ok"}


@router.post(
    "/projects",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
)
def create_project(payload: ProjectCreate, request: Request) -> Project:
    """Create a project."""

    return get_repository(request).create_project(payload)


@router.get("/projects", response_model=list[Project])
def list_projects(request: Request) -> list[Project]:
    """List projects."""

    return get_repository(request).list_projects()


@router.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: str, request: Request) -> Project:
    """Get a project."""

    try:
        return get_repository(request).get_project(project_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.post(
    "/sessions",
    response_model=ResearchSession,
    status_code=status.HTTP_201_CREATED,
)
def create_session(payload: SessionCreate, request: Request) -> ResearchSession:
    """Create a session and initial root branch."""

    try:
        return get_repository(request).create_session(payload)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.get("/sessions", response_model=list[ResearchSession])
def list_sessions(request: Request) -> list[ResearchSession]:
    """List sessions."""

    return get_repository(request).list_sessions()


@router.get("/sessions/{session_id}", response_model=ResearchSession)
def get_session(session_id: str, request: Request) -> ResearchSession:
    """Get a session."""

    try:
        return get_repository(request).get_session(session_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.get("/sessions/{session_id}/state", response_model=SessionSnapshot)
def get_session_state(session_id: str, request: Request) -> SessionSnapshot:
    """Get reconstructable session state."""

    try:
        return get_repository(request).get_session_snapshot(session_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.get("/sessions/{session_id}/loop", response_model=RuntimeLoopBinding)
def get_session_loop(session_id: str, request: Request) -> RuntimeLoopBinding:
    """Get the runtime research-loop binding for a session."""

    try:
        return get_repository(request).get_runtime_loop_binding(session_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.post("/sessions/{session_id}/start", response_model=ResearchSession)
def start_session(session_id: str, request: Request) -> ResearchSession:
    """Mark a session as running without executing research work inline."""

    try:
        return get_repository(request).set_session_status(
            session_id,
            SessionStatus.RUNNING,
            "session_started",
        )
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.post("/sessions/{session_id}/pause", response_model=ResearchSession)
def pause_session(session_id: str, request: Request) -> ResearchSession:
    """Pause a running session."""

    try:
        return get_repository(request).set_session_status(
            session_id,
            SessionStatus.PAUSED,
            "session_paused",
        )
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.post("/sessions/{session_id}/resume", response_model=ResearchSession)
def resume_session(session_id: str, request: Request) -> ResearchSession:
    """Resume a paused session."""

    try:
        return get_repository(request).set_session_status(
            session_id,
            SessionStatus.RUNNING,
            "session_resumed",
        )
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.post("/sessions/{session_id}/cancel", response_model=ResearchSession)
def cancel_session(session_id: str, request: Request) -> ResearchSession:
    """Cancel a session."""

    try:
        return get_repository(request).set_session_status(
            session_id,
            SessionStatus.CANCELLED,
            "session_cancelled",
        )
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.get("/sessions/{session_id}/branches", response_model=list[Branch])
def list_session_branches(session_id: str, request: Request) -> list[Branch]:
    """List branches for a session."""

    try:
        return get_repository(request).list_branches(session_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.get("/branches/{branch_id}", response_model=Branch)
def get_branch(branch_id: str, request: Request) -> Branch:
    """Get a branch."""

    try:
        return get_repository(request).get_branch(branch_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.post("/branches/{branch_id}/continue", response_model=Branch)
def continue_branch(branch_id: str, request: Request) -> Branch:
    """Request continuation for a branch without running work inline."""

    try:
        return get_repository(request).continue_branch(branch_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.post("/branches/{branch_id}/split", response_model=list[Branch])
def split_branch(
    branch_id: str,
    payload: BranchSplitRequest,
    request: Request,
) -> list[Branch]:
    """Split a branch into child branches."""

    if not payload.branches:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one child branch is required",
        )

    try:
        return get_repository(request).split_branch(branch_id, payload.branches)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.post("/branches/{branch_id}/prune", response_model=Branch)
def prune_branch(branch_id: str, request: Request) -> Branch:
    """Prune a branch."""

    try:
        return get_repository(request).prune_branch(branch_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.patch("/branches/{branch_id}", response_model=Branch)
def update_branch(
    branch_id: str,
    payload: BranchPatch,
    request: Request,
) -> Branch:
    """Update branch metadata."""

    try:
        return get_repository(request).update_branch(branch_id, payload)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.get("/sessions/{session_id}/papers", response_model=list[Paper])
def list_session_papers(session_id: str, request: Request) -> list[Paper]:
    """List papers for a session."""

    try:
        return get_repository(request).list_papers(session_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.get("/papers/{paper_id}", response_model=Paper)
def get_paper(paper_id: str, request: Request) -> Paper:
    """Get a paper."""

    try:
        return get_repository(request).get_paper(paper_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise


@router.get("/sessions/{session_id}/events", response_model=list[Event])
def list_session_events(session_id: str, request: Request) -> list[Event]:
    """List events for a session."""

    try:
        return get_repository(request).list_events(session_id)
    except RepositoryError as exc:
        handle_repository_error(exc)
        raise
