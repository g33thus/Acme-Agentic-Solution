"""FastAPI entry point.

Phase 0 stands up the app with the unauthenticated /health endpoint so the
Docker Compose stack is bootable and verifiable. Query, session, and auth
routes are added in Phase 3 (see specs/tasks.md and specs/api/openapi.yaml).
"""

from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Acme Operations Agentic Assistant API",
    version=settings.app_version,
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Unauthenticated liveness check. The only public endpoint."""
    return {"status": "ok", "version": settings.app_version}
