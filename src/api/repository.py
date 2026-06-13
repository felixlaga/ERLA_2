"""Temporary in-memory repository for the ERLA product API skeleton."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from typing import TYPE_CHECKING
from uuid import uuid4

from .models import (
    Branch,
    BranchCreate,
    BranchPatch,
    BranchStatus,
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
from .research_loop import ResearchLoopBridge

if TYPE_CHECKING:
    from ..orchestration.models import LoopState


class RepositoryError(Exception):
    """Base repository error."""


class NotFoundError(RepositoryError):
    """Raised when an entity cannot be found."""


class ConflictError(RepositoryError):
    """Raised when a requested state transition is invalid."""


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class InMemoryRepository:
    """Process-local repository used until durable storage is added."""

    def __init__(self, loop_bridge: ResearchLoopBridge | None = None) -> None:
        self._projects: dict[str, Project] = {}
        self._sessions: dict[str, ResearchSession] = {}
        self._branches: dict[str, Branch] = {}
        self._papers: dict[str, Paper] = {}
        self._events: dict[str, Event] = {}
        self._runtime_loop_bindings: dict[str, RuntimeLoopBinding] = {}
        self._runtime_loop_states: dict[str, LoopState] = {}
        self._loop_bridge = loop_bridge or ResearchLoopBridge()
        self._lock = Lock()

    def create_project(self, payload: ProjectCreate) -> Project:
        """Create a project."""

        with self._lock:
            now = utc_now()
            project = Project(
                id=self._new_id("proj"),
                title=payload.title,
                description=payload.description,
                field=payload.field,
                settings=deepcopy(payload.settings),
                created_at=now,
                updated_at=now,
            )
            self._projects[project.id] = project
            return project

    def list_projects(self) -> list[Project]:
        """List projects."""

        with self._lock:
            return list(self._projects.values())

    def get_project(self, project_id: str) -> Project:
        """Get a project."""

        with self._lock:
            try:
                return self._projects[project_id]
            except KeyError as exc:
                raise NotFoundError("Project not found") from exc

    def create_session(self, payload: SessionCreate) -> ResearchSession:
        """Create a research session and root branch."""

        with self._lock:
            if payload.project_id and payload.project_id not in self._projects:
                raise NotFoundError("Project not found")

            now = utc_now()
            session = ResearchSession(
                id=self._new_id("sess"),
                project_id=payload.project_id,
                initial_query=payload.initial_query,
                source_providers=list(payload.source_providers),
                filters=deepcopy(payload.filters),
                parameters=deepcopy(payload.parameters),
                status=SessionStatus.PENDING,
                created_at=now,
                updated_at=now,
            )
            self._sessions[session.id] = session

            runtime_loop = self._loop_bridge.create_loop(session)
            root_branch = self._loop_bridge.to_api_branch(
                session_id=session.id,
                runtime_branch=runtime_loop.root_branch,
                label="Root",
                rationale="Initial session query.",
                created_at=now,
                updated_at=now,
            )
            self._branches[root_branch.id] = root_branch
            self._runtime_loop_states[session.id] = runtime_loop.state
            self._runtime_loop_bindings[session.id] = RuntimeLoopBinding(
                session_id=session.id,
                loop_id=runtime_loop.state.loop_id,
                loop_number=runtime_loop.state.loop_number,
                root_branch_id=runtime_loop.root_branch.id,
                created_at=now,
                updated_at=now,
            )

            self._create_event_unlocked(
                session_id=session.id,
                event_type="session_created",
                payload={"initial_query": session.initial_query},
            )
            self._create_event_unlocked(
                session_id=session.id,
                event_type="research_loop_created",
                payload={
                    "loop_id": runtime_loop.state.loop_id,
                    "loop_number": runtime_loop.state.loop_number,
                    "root_branch_id": runtime_loop.root_branch.id,
                },
            )
            self._create_event_unlocked(
                session_id=session.id,
                branch_id=root_branch.id,
                event_type="branch_created",
                payload={"query": root_branch.query, "parent_branch_id": None},
            )
            return session

    def list_sessions(self) -> list[ResearchSession]:
        """List sessions."""

        with self._lock:
            return list(self._sessions.values())

    def get_session(self, session_id: str) -> ResearchSession:
        """Get a session."""

        with self._lock:
            return self._get_session_unlocked(session_id)

    def get_session_snapshot(self, session_id: str) -> SessionSnapshot:
        """Get reconstructable session state."""

        with self._lock:
            session = self._get_session_unlocked(session_id)
            return SessionSnapshot(
                session=session,
                runtime_loop=self._runtime_loop_bindings.get(session_id),
                branches=self._list_branches_unlocked(session_id),
                papers=self._list_papers_unlocked(session_id),
                events=self._list_events_unlocked(session_id),
            )

    def get_runtime_loop_binding(self, session_id: str) -> RuntimeLoopBinding:
        """Get the runtime loop binding for a session."""

        with self._lock:
            self._get_session_unlocked(session_id)
            try:
                return self._runtime_loop_bindings[session_id]
            except KeyError as exc:
                raise NotFoundError("Runtime loop not found") from exc

    def set_session_status(
        self,
        session_id: str,
        status: SessionStatus,
        event_type: str,
    ) -> ResearchSession:
        """Set a session status for run-control endpoints."""

        with self._lock:
            session = self._get_session_unlocked(session_id)
            self._validate_session_transition(session.status, status)

            now = utc_now()
            session.status = status
            session.updated_at = now
            if status == SessionStatus.RUNNING and session.started_at is None:
                session.started_at = now
            if status in {
                SessionStatus.COMPLETED,
                SessionStatus.CANCELLED,
                SessionStatus.FAILED,
            }:
                session.completed_at = now
            self._sessions[session.id] = session

            if status == SessionStatus.RUNNING:
                for branch in self._list_branches_unlocked(session.id):
                    if branch.status in {BranchStatus.PENDING, BranchStatus.PAUSED}:
                        branch.status = BranchStatus.RUNNING
                        branch.updated_at = now
                        self._branches[branch.id] = branch

            if status == SessionStatus.PAUSED:
                for branch in self._list_branches_unlocked(session.id):
                    if branch.status == BranchStatus.RUNNING:
                        branch.status = BranchStatus.PAUSED
                        branch.updated_at = now
                        self._branches[branch.id] = branch

            event_payload = {"status": status.value}
            binding = self._runtime_loop_bindings.get(session.id)
            if binding:
                event_payload.update(
                    {
                        "loop_id": binding.loop_id,
                        "root_branch_id": binding.root_branch_id,
                    }
                )

            self._create_event_unlocked(
                session_id=session.id,
                event_type=event_type,
                payload=event_payload,
            )
            return session

    def list_branches(self, session_id: str) -> list[Branch]:
        """List branches for a session."""

        with self._lock:
            self._get_session_unlocked(session_id)
            return self._list_branches_unlocked(session_id)

    def get_branch(self, branch_id: str) -> Branch:
        """Get a branch."""

        with self._lock:
            return self._get_branch_unlocked(branch_id)

    def continue_branch(self, branch_id: str) -> Branch:
        """Record a request to continue a branch without running work inline."""

        with self._lock:
            branch = self._get_branch_unlocked(branch_id)
            if branch.status == BranchStatus.PRUNED:
                raise ConflictError("Cannot continue a pruned branch")

            branch.status = BranchStatus.RUNNING
            branch.updated_at = utc_now()
            self._branches[branch.id] = branch
            self._create_event_unlocked(
                session_id=branch.session_id,
                branch_id=branch.id,
                event_type="branch_continue_requested",
                payload={"query": branch.query},
            )
            return branch

    def split_branch(
        self,
        branch_id: str,
        branch_payloads: list[BranchCreate],
    ) -> list[Branch]:
        """Create child branches from a parent branch."""

        with self._lock:
            parent = self._get_branch_unlocked(branch_id)
            if parent.status == BranchStatus.PRUNED:
                raise ConflictError("Cannot split a pruned branch")

            now = utc_now()
            children: list[Branch] = []
            for payload in branch_payloads:
                child = Branch(
                    id=self._new_id("branch"),
                    session_id=parent.session_id,
                    parent_branch_id=parent.id,
                    query=payload.query,
                    label=payload.label,
                    rationale=payload.rationale,
                    mode=payload.mode,
                    status=BranchStatus.PENDING,
                    depth=parent.depth + 1,
                    created_at=now,
                    updated_at=now,
                )
                self._branches[child.id] = child
                children.append(child)

            self._create_event_unlocked(
                session_id=parent.session_id,
                branch_id=parent.id,
                event_type="branch_split",
                payload={"child_branch_ids": [child.id for child in children]},
            )
            return children

    def prune_branch(self, branch_id: str) -> Branch:
        """Prune a branch."""

        with self._lock:
            branch = self._get_branch_unlocked(branch_id)
            branch.status = BranchStatus.PRUNED
            branch.updated_at = utc_now()
            self._branches[branch.id] = branch
            self._create_event_unlocked(
                session_id=branch.session_id,
                branch_id=branch.id,
                event_type="branch_pruned",
                payload={"query": branch.query},
            )
            return branch

    def update_branch(self, branch_id: str, payload: BranchPatch) -> Branch:
        """Update branch metadata."""

        with self._lock:
            branch = self._get_branch_unlocked(branch_id)
            update = payload.model_dump(exclude_unset=True)
            event_payload = payload.model_dump(exclude_unset=True, mode="json")
            for field_name, value in update.items():
                setattr(branch, field_name, value)
            branch.updated_at = utc_now()
            self._branches[branch.id] = branch
            self._create_event_unlocked(
                session_id=branch.session_id,
                branch_id=branch.id,
                event_type="branch_updated",
                payload=event_payload,
            )
            return branch

    def list_papers(self, session_id: str) -> list[Paper]:
        """List papers for a session."""

        with self._lock:
            self._get_session_unlocked(session_id)
            return self._list_papers_unlocked(session_id)

    def get_paper(self, paper_id: str) -> Paper:
        """Get a paper by internal API ID or provider paper ID."""

        with self._lock:
            for paper in self._papers.values():
                if paper.id == paper_id or paper.paper_id == paper_id:
                    return paper
            raise NotFoundError("Paper not found")

    def list_events(self, session_id: str) -> list[Event]:
        """List session events."""

        with self._lock:
            self._get_session_unlocked(session_id)
            return self._list_events_unlocked(session_id)

    def _get_session_unlocked(self, session_id: str) -> ResearchSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise NotFoundError("Session not found") from exc

    def _get_branch_unlocked(self, branch_id: str) -> Branch:
        try:
            return self._branches[branch_id]
        except KeyError as exc:
            raise NotFoundError("Branch not found") from exc

    def _list_branches_unlocked(self, session_id: str) -> list[Branch]:
        return [
            branch
            for branch in self._branches.values()
            if branch.session_id == session_id
        ]

    def _list_papers_unlocked(self, session_id: str) -> list[Paper]:
        return [
            paper
            for paper in self._papers.values()
            if paper.session_id == session_id
        ]

    def _list_events_unlocked(self, session_id: str) -> list[Event]:
        events = [
            event
            for event in self._events.values()
            if event.session_id == session_id
        ]
        return sorted(events, key=lambda event: event.created_at)

    def _create_event_unlocked(
        self,
        session_id: str,
        event_type: str,
        payload: dict,
        branch_id: str | None = None,
        paper_id: str | None = None,
        severity: str = "info",
    ) -> Event:
        event = Event(
            id=self._new_id("evt"),
            session_id=session_id,
            branch_id=branch_id,
            paper_id=paper_id,
            event_type=event_type,
            payload=payload,
            severity=severity,
            created_at=utc_now(),
        )
        self._events[event.id] = event
        return event

    def _validate_session_transition(
        self,
        current: SessionStatus,
        target: SessionStatus,
    ) -> None:
        if current in {SessionStatus.COMPLETED, SessionStatus.CANCELLED}:
            raise ConflictError(f"Session is already {current.value}")
        if target == SessionStatus.PAUSED and current != SessionStatus.RUNNING:
            raise ConflictError("Only running sessions can be paused")
        if target == SessionStatus.RUNNING and current == SessionStatus.FAILED:
            raise ConflictError("Failed sessions cannot be resumed in the API skeleton")

    def _new_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:12]}"
