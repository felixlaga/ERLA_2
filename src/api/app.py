"""FastAPI application factory for the ERLA product API skeleton."""

from __future__ import annotations

from fastapi import FastAPI

from .repository import InMemoryRepository
from .routes import router


def create_app(repository: InMemoryRepository | None = None) -> FastAPI:
    """Create the ERLA product API app."""

    app = FastAPI(
        title="ERLA Product API",
        version="0.1.0",
        description=(
            "Skeleton API boundary for ERLA projects, sessions, branches, "
            "papers, events, and run controls."
        ),
    )
    app.state.repository = repository or InMemoryRepository()
    app.include_router(router)
    return app


app = create_app()
