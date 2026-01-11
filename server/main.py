"""
Nexus - FastAPI Main Application
=================================

Main entry point for the Nexus autonomous coding platform.
Provides REST API, WebSocket, and static file serving.
"""

import shutil
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import (
    agent_router,
    assistant_chat_router,
    auth_router,
    features_router,
    filesystem_router,
    projects_router,
    settings_router,
    spec_creation_router,
)
from .routers.agents import router as multi_agent_router
from .routers.worktrees import router as worktrees_router
from .routers.assets import router as assets_router
from .routers.config import router as config_router
from .routers.questions import router as questions_router
from .schemas import SetupStatus
from .services.assistant_chat_session import cleanup_all_sessions as cleanup_assistant_sessions
from .services.process_manager import cleanup_all_managers, cleanup_orphaned_locks
from .websocket import project_websocket

# Paths
ROOT_DIR = Path(__file__).parent.parent
UI_DIST_DIR = ROOT_DIR / "ui" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup - clean up orphaned lock files from previous runs
    cleanup_orphaned_locks()

    # Startup - clean up stale projects (paths that no longer exist)
    try:
        import sys
        if str(ROOT_DIR) not in sys.path:
            sys.path.insert(0, str(ROOT_DIR))
        from registry import cleanup_stale_projects
        removed = cleanup_stale_projects()
        if removed:
            import logging
            logging.getLogger(__name__).info(
                "Cleaned up %d stale project(s): %s", len(removed), removed
            )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Failed to cleanup stale projects: %s", e)

    yield
    # Shutdown - cleanup all running agents and assistant sessions
    await cleanup_all_managers()
    await cleanup_assistant_sessions()


# Create FastAPI app
app = FastAPI(
    title="Nexus",
    description="Autonomous coding platform powered by Claude",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS - allow only localhost origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:8888",      # Production
        "http://127.0.0.1:8888",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Security Middleware
# ============================================================================

@app.middleware("http")
async def require_localhost(request: Request, call_next):
    """Only allow requests from localhost."""
    client_host = request.client.host if request.client else None

    # Allow localhost connections
    if client_host not in ("127.0.0.1", "::1", "localhost", None):
        raise HTTPException(status_code=403, detail="Localhost access only")

    return await call_next(request)


# ============================================================================
# Include Routers
# ============================================================================

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(features_router)
app.include_router(agent_router)
app.include_router(spec_creation_router)
app.include_router(filesystem_router)
app.include_router(assistant_chat_router)
app.include_router(settings_router)

# New routers for enhanced project management
app.include_router(multi_agent_router)
app.include_router(worktrees_router)
app.include_router(assets_router)
app.include_router(config_router)
app.include_router(questions_router)


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws/projects/{project_name}")
async def websocket_endpoint(websocket: WebSocket, project_name: str):
    """WebSocket endpoint for real-time project updates."""
    await project_websocket(websocket, project_name)


# ============================================================================
# Setup & Health Endpoints
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/setup/status", response_model=SetupStatus)
async def setup_status():
    """Check system setup status."""
    # Check for Claude CLI
    claude_cli = shutil.which("claude") is not None

    # Check for credentials file
    credentials_path = Path.home() / ".claude" / ".credentials.json"
    credentials = credentials_path.exists()

    # Check for Node.js and npm
    node = shutil.which("node") is not None
    npm = shutil.which("npm") is not None

    return SetupStatus(
        claude_cli=claude_cli,
        credentials=credentials,
        node=node,
        npm=npm,
    )


# ============================================================================
# Static File Serving (Production)
# ============================================================================

# Serve React build files if they exist
if UI_DIST_DIR.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=UI_DIST_DIR / "assets"), name="assets")

    @app.get("/")
    async def serve_index():
        """Serve the React app index.html."""
        return FileResponse(UI_DIST_DIR / "index.html")

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """
        Serve static files or fall back to index.html for SPA routing.
        """
        # Check if the path is an API route (shouldn't hit this due to router ordering)
        if path.startswith("api/") or path.startswith("ws/"):
            raise HTTPException(status_code=404)

        # Try to serve the file directly
        file_path = UI_DIST_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Fall back to index.html for SPA routing
        return FileResponse(UI_DIST_DIR / "index.html")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",  # Localhost only for security
        port=8888,
        reload=True,
    )
