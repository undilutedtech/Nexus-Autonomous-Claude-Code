"""
Projects Router
===============

API endpoints for project management.
Uses project registry for path lookups instead of fixed generations/ directory.
"""

import re
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectPrompts,
    ProjectPromptsUpdate,
    ProjectStats,
    ProjectSummary,
    ProjectUsageStats,
    SessionUsageResponse,
)

# Lazy imports to avoid circular dependencies
_imports_initialized = False
_check_spec_exists = None
_scaffold_project_prompts = None
_get_project_prompts_dir = None
_count_passing_tests = None
_load_usage_stats = None


def _init_imports():
    """Lazy import of project-level modules."""
    global _imports_initialized, _check_spec_exists
    global _scaffold_project_prompts, _get_project_prompts_dir
    global _count_passing_tests, _load_usage_stats

    if _imports_initialized:
        return

    import sys
    root = Path(__file__).parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from progress import count_passing_tests
    from prompts import get_project_prompts_dir, scaffold_project_prompts
    from start import check_spec_exists
    from usage_tracking import load_usage_stats

    _check_spec_exists = check_spec_exists
    _scaffold_project_prompts = scaffold_project_prompts
    _get_project_prompts_dir = get_project_prompts_dir
    _count_passing_tests = count_passing_tests
    _load_usage_stats = load_usage_stats
    _imports_initialized = True


def _get_registry_functions():
    """Get registry functions with lazy import."""
    import sys
    root = Path(__file__).parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from registry import (
        get_project_path,
        list_registered_projects,
        register_project,
        unregister_project,
        validate_project_path,
        update_project_status,
        get_project_by_status,
        get_all_projects_stats,
    )
    return (
        register_project,
        unregister_project,
        get_project_path,
        list_registered_projects,
        validate_project_path,
        update_project_status,
        get_project_by_status,
        get_all_projects_stats,
    )


router = APIRouter(prefix="/api/projects", tags=["projects"])


def validate_project_name(name: str) -> str:
    """Validate and sanitize project name to prevent path traversal."""
    if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', name):
        raise HTTPException(
            status_code=400,
            detail="Invalid project name. Use only letters, numbers, hyphens, and underscores (1-50 chars)."
        )
    return name


def get_project_stats(project_dir: Path) -> ProjectStats:
    """Get statistics for a project."""
    _init_imports()
    passing, in_progress, total = _count_passing_tests(project_dir)
    percentage = (passing / total * 100) if total > 0 else 0.0
    return ProjectStats(
        passing=passing,
        in_progress=in_progress,
        total=total,
        percentage=round(percentage, 1)
    )


@router.get("", response_model=list[ProjectSummary])
async def list_projects():
    """List all registered projects."""
    _init_imports()
    _, _, _, list_registered_projects, validate_project_path, *_ = _get_registry_functions()

    projects = list_registered_projects()
    result = []

    for name, info in projects.items():
        project_dir = Path(info["path"])

        # Skip if path no longer exists
        is_valid, _ = validate_project_path(project_dir)
        if not is_valid:
            continue

        has_spec = _check_spec_exists(project_dir)
        stats = get_project_stats(project_dir)

        result.append(ProjectSummary(
            name=name,
            path=info["path"],
            has_spec=has_spec,
            stats=stats,
            status=info.get("status", "active"),
        ))

    return result


@router.post("", response_model=ProjectSummary)
async def create_project(project: ProjectCreate):
    """Create a new project at the specified path."""
    _init_imports()
    register_project, unregister_project, get_project_path, *_ = _get_registry_functions()

    name = validate_project_name(project.name)
    project_path = Path(project.path).resolve()

    # Check if project name already registered
    existing = get_project_path(name)
    if existing:
        # Check if the existing path still exists
        if Path(existing).exists():
            raise HTTPException(
                status_code=409,
                detail=f"Project '{name}' already exists at {existing}"
            )
        # Old path doesn't exist - unregister so we can re-register with new path
        unregister_project(name)

    # Security: Check if path is in a blocked location
    from .filesystem import is_path_blocked
    if is_path_blocked(project_path):
        raise HTTPException(
            status_code=403,
            detail="Cannot create project in system or sensitive directory"
        )

    # Validate the path is usable
    if project_path.exists():
        if not project_path.is_dir():
            raise HTTPException(
                status_code=400,
                detail="Path exists but is not a directory"
            )
    else:
        # Create the directory
        try:
            project_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create directory: {e}"
            )

    # Scaffold prompts
    _scaffold_project_prompts(project_path)

    # Register in registry
    try:
        register_project(name, project_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register project: {e}"
        )

    return ProjectSummary(
        name=name,
        path=project_path.as_posix(),
        has_spec=False,  # Just created, no spec yet
        stats=ProjectStats(passing=0, total=0, percentage=0.0),
    )


# =============================================================================
# Static routes must come before parameterized routes
# =============================================================================

class ProjectOverviewStats(BaseModel):
    """Overview statistics for all projects."""
    total_projects: int
    active_projects: int
    paused_projects: int
    finished_projects: int
    total_features: int
    total_passing: int
    overall_percentage: float
    # Active projects only stats
    active_features: int = 0
    active_passing: int = 0
    active_percentage: float = 0.0
    active_in_progress: int = 0


@router.get("/overview", response_model=ProjectOverviewStats)
async def get_projects_overview():
    """
    Get aggregate statistics across all projects.

    Returns counts of projects by status and overall feature progress.
    Includes separate stats for active (in-progress) projects only.
    """
    _init_imports()
    funcs = _get_registry_functions()
    list_registered_projects = funcs[3]
    validate_project_path = funcs[4]

    projects = list_registered_projects()

    total_projects = 0
    active_projects = 0
    paused_projects = 0
    finished_projects = 0
    total_features = 0
    total_passing = 0
    # Active projects only
    active_features = 0
    active_passing = 0
    active_in_progress = 0

    for name, info in projects.items():
        project_dir = Path(info["path"])

        # Skip if path no longer exists
        is_valid, _ = validate_project_path(project_dir)
        if not is_valid:
            continue

        total_projects += 1

        # Get project status
        status = info.get("status", "active")
        if status == "active":
            active_projects += 1
        elif status == "paused":
            paused_projects += 1
        elif status == "finished":
            finished_projects += 1

        # Get feature stats
        stats = get_project_stats(project_dir)
        total_features += stats.total
        total_passing += stats.passing

        # Track active projects stats separately
        if status == "active":
            active_features += stats.total
            active_passing += stats.passing
            active_in_progress += stats.in_progress

    overall_percentage = (total_passing / total_features * 100) if total_features > 0 else 0.0
    active_percentage = (active_passing / active_features * 100) if active_features > 0 else 0.0

    return ProjectOverviewStats(
        total_projects=total_projects,
        active_projects=active_projects,
        paused_projects=paused_projects,
        finished_projects=finished_projects,
        total_features=total_features,
        total_passing=total_passing,
        overall_percentage=round(overall_percentage, 1),
        active_features=active_features,
        active_passing=active_passing,
        active_percentage=round(active_percentage, 1),
        active_in_progress=active_in_progress,
    )


class AggregateUsageStats(BaseModel):
    """Aggregate usage statistics across all projects."""
    total_projects_with_usage: int = 0
    total_sessions: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_read_tokens: int = 0
    total_cache_creation_tokens: int = 0
    total_cost_usd: float = 0.0
    total_duration_ms: int = 0
    total_tokens: int = 0
    avg_cost_per_project: float = 0.0
    avg_sessions_per_project: float = 0.0
    # Per-project breakdown
    projects: list[dict] = []


@router.get("/analytics/usage", response_model=AggregateUsageStats)
async def get_aggregate_usage_stats():
    """
    Get aggregate usage statistics across all projects.

    Returns total tokens, costs, and per-project breakdown.
    """
    _init_imports()
    funcs = _get_registry_functions()
    list_registered_projects = funcs[3]
    validate_project_path = funcs[4]

    projects = list_registered_projects()

    total_sessions = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_read_tokens = 0
    total_cache_creation_tokens = 0
    total_cost_usd = 0.0
    total_duration_ms = 0
    total_tokens = 0
    projects_with_usage = 0
    project_stats = []

    for name, info in projects.items():
        project_dir = Path(info["path"])

        is_valid, _ = validate_project_path(project_dir)
        if not is_valid:
            continue

        try:
            stats = _load_usage_stats(project_dir)
            if stats.total_sessions > 0:
                projects_with_usage += 1
                total_sessions += stats.total_sessions
                total_input_tokens += stats.total_input_tokens
                total_output_tokens += stats.total_output_tokens
                total_cache_read_tokens += stats.total_cache_read_tokens
                total_cache_creation_tokens += stats.total_cache_creation_tokens
                total_cost_usd += stats.total_cost_usd
                total_duration_ms += stats.total_duration_ms
                total_tokens += stats.total_tokens

                project_stats.append({
                    "name": name,
                    "status": info.get("status", "active"),
                    "sessions": stats.total_sessions,
                    "tokens": stats.total_tokens,
                    "cost_usd": round(stats.total_cost_usd, 4),
                    "duration_hours": round(stats.total_duration_ms / 3600000, 2),
                })
        except Exception:
            continue

    avg_cost = total_cost_usd / projects_with_usage if projects_with_usage > 0 else 0
    avg_sessions = total_sessions / projects_with_usage if projects_with_usage > 0 else 0

    # Sort projects by cost descending
    project_stats.sort(key=lambda x: x["cost_usd"], reverse=True)

    return AggregateUsageStats(
        total_projects_with_usage=projects_with_usage,
        total_sessions=total_sessions,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        total_cache_read_tokens=total_cache_read_tokens,
        total_cache_creation_tokens=total_cache_creation_tokens,
        total_cost_usd=round(total_cost_usd, 4),
        total_duration_ms=total_duration_ms,
        total_tokens=total_tokens,
        avg_cost_per_project=round(avg_cost, 4),
        avg_sessions_per_project=round(avg_sessions, 1),
        projects=project_stats,
    )


@router.get("/by-status/{status}", response_model=list[ProjectSummary])
async def get_projects_by_status(status: str):
    """
    Get projects filtered by status.

    Valid statuses: active, paused, finished, archived
    """
    _init_imports()
    funcs = _get_registry_functions()
    get_project_by_status = funcs[6]
    validate_project_path = funcs[4]

    valid_statuses = {"active", "paused", "finished", "archived"}
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    projects = get_project_by_status(status)
    result = []

    for name, info in projects.items():
        project_dir = Path(info["path"])

        # Skip if path no longer exists
        is_valid, _ = validate_project_path(project_dir)
        if not is_valid:
            continue

        has_spec = _check_spec_exists(project_dir)
        stats = get_project_stats(project_dir)

        result.append(ProjectSummary(
            name=name,
            path=info["path"],
            has_spec=has_spec,
            stats=stats,
            status=info.get("status", "active"),
        ))

    return result


# =============================================================================
# Parameterized project routes
# =============================================================================

@router.get("/{name}", response_model=ProjectDetail)
async def get_project(name: str):
    """Get detailed information about a project."""
    _init_imports()
    _, _, get_project_path, *_ = _get_registry_functions()

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project directory no longer exists: {project_dir}")

    has_spec = _check_spec_exists(project_dir)
    stats = get_project_stats(project_dir)
    prompts_dir = _get_project_prompts_dir(project_dir)

    return ProjectDetail(
        name=name,
        path=project_dir.as_posix(),
        has_spec=has_spec,
        stats=stats,
        prompts_dir=str(prompts_dir),
    )


@router.delete("/{name}")
async def delete_project(name: str, delete_files: bool = False):
    """
    Delete a project from the registry.

    Args:
        name: Project name to delete
        delete_files: If True, also delete the project directory and files
    """
    _init_imports()
    _, unregister_project, get_project_path, *_ = _get_registry_functions()

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    # Check if agent is running
    lock_file = project_dir / ".agent.lock"
    if lock_file.exists():
        raise HTTPException(
            status_code=409,
            detail="Cannot delete project while agent is running. Stop the agent first."
        )

    # Optionally delete files
    if delete_files and project_dir.exists():
        try:
            shutil.rmtree(project_dir)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete project files: {e}")

    # Unregister from registry
    unregister_project(name)

    return {
        "success": True,
        "message": f"Project '{name}' deleted" + (" (files removed)" if delete_files else " (files preserved)")
    }


@router.get("/{name}/prompts", response_model=ProjectPrompts)
async def get_project_prompts(name: str):
    """Get the content of project prompt files."""
    _init_imports()
    _, _, get_project_path, *_ = _get_registry_functions()

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    prompts_dir = _get_project_prompts_dir(project_dir)

    def read_file(filename: str) -> str:
        filepath = prompts_dir / filename
        if filepath.exists():
            try:
                return filepath.read_text(encoding="utf-8")
            except Exception:
                return ""
        return ""

    return ProjectPrompts(
        app_spec=read_file("app_spec.txt"),
        initializer_prompt=read_file("initializer_prompt.md"),
        coding_prompt=read_file("coding_prompt.md"),
    )


@router.put("/{name}/prompts")
async def update_project_prompts(name: str, prompts: ProjectPromptsUpdate):
    """Update project prompt files."""
    _init_imports()
    _, _, get_project_path, *_ = _get_registry_functions()

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    prompts_dir = _get_project_prompts_dir(project_dir)
    prompts_dir.mkdir(parents=True, exist_ok=True)

    def write_file(filename: str, content: str | None):
        if content is not None:
            filepath = prompts_dir / filename
            filepath.write_text(content, encoding="utf-8")

    write_file("app_spec.txt", prompts.app_spec)
    write_file("initializer_prompt.md", prompts.initializer_prompt)
    write_file("coding_prompt.md", prompts.coding_prompt)

    return {"success": True, "message": "Prompts updated"}


@router.get("/{name}/stats", response_model=ProjectStats)
async def get_project_stats_endpoint(name: str):
    """Get current progress statistics for a project."""
    _init_imports()
    _, _, get_project_path, *_ = _get_registry_functions()

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    return get_project_stats(project_dir)


@router.get("/{name}/usage", response_model=ProjectUsageStats)
async def get_project_usage_stats(name: str):
    """Get token usage and cost statistics for a project."""
    _init_imports()
    _, _, get_project_path, *_ = _get_registry_functions()

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    # Load usage stats from the project
    stats = _load_usage_stats(project_dir)

    # Convert sessions to response format (most recent 10)
    recent_sessions = []
    for session in reversed(stats.sessions[-10:]):
        recent_sessions.append(SessionUsageResponse(
            session_id=session.session_id,
            model=session.model,
            input_tokens=session.input_tokens,
            output_tokens=session.output_tokens,
            cache_read_tokens=session.cache_read_tokens,
            cache_creation_tokens=session.cache_creation_tokens,
            cost_usd=session.cost_usd,
            duration_ms=session.duration_ms,
            duration_api_ms=session.duration_api_ms,
            num_turns=session.num_turns,
            timestamp=session.timestamp,
        ))

    # Calculate averages
    avg_tokens = stats.total_tokens / stats.total_sessions if stats.total_sessions > 0 else 0
    avg_cost = stats.total_cost_usd / stats.total_sessions if stats.total_sessions > 0 else 0
    avg_duration = stats.total_duration_ms / stats.total_sessions if stats.total_sessions > 0 else 0

    return ProjectUsageStats(
        total_sessions=stats.total_sessions,
        total_input_tokens=stats.total_input_tokens,
        total_output_tokens=stats.total_output_tokens,
        total_cache_read_tokens=stats.total_cache_read_tokens,
        total_cache_creation_tokens=stats.total_cache_creation_tokens,
        total_cost_usd=stats.total_cost_usd,
        total_duration_ms=stats.total_duration_ms,
        total_tokens=stats.total_tokens,
        avg_tokens_per_session=round(avg_tokens, 1),
        avg_cost_per_session=round(avg_cost, 4),
        avg_duration_per_session=round(avg_duration, 1),
        recent_sessions=recent_sessions,
    )


# =============================================================================
# Project Lifecycle Endpoints
# =============================================================================

class ProjectStatusResponse(BaseModel):
    """Response after status change."""
    success: bool
    project_name: str
    status: str
    message: str


@router.post("/{name}/pause", response_model=ProjectStatusResponse)
async def pause_project(name: str):
    """
    Pause a project.

    Stops all running agents and marks the project as paused.
    """
    _init_imports()
    funcs = _get_registry_functions()
    get_project_path = funcs[2]
    update_project_status = funcs[5]

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    # Stop any running agents
    from ..services.multi_agent_manager import get_multi_manager
    try:
        manager = await get_multi_manager(name, project_dir)
        await manager.stop_all()
    except Exception:
        pass  # Manager might not exist

    # Update status
    update_project_status(name, "paused")

    return ProjectStatusResponse(
        success=True,
        project_name=name,
        status="paused",
        message=f"Project '{name}' paused"
    )


@router.post("/{name}/resume", response_model=ProjectStatusResponse)
async def resume_project(name: str):
    """
    Resume a paused project.

    Marks the project as active so agents can be started.
    """
    _init_imports()
    funcs = _get_registry_functions()
    get_project_path = funcs[2]
    update_project_status = funcs[5]

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    # Update status
    update_project_status(name, "active")

    return ProjectStatusResponse(
        success=True,
        project_name=name,
        status="active",
        message=f"Project '{name}' resumed"
    )


@router.post("/{name}/finish", response_model=ProjectStatusResponse)
async def finish_project(name: str):
    """
    Mark a project as finished.

    Stops all agents and marks the project as complete.
    """
    _init_imports()
    funcs = _get_registry_functions()
    get_project_path = funcs[2]
    update_project_status = funcs[5]

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    # Stop any running agents
    from ..services.multi_agent_manager import get_multi_manager
    try:
        manager = await get_multi_manager(name, project_dir)
        await manager.stop_all()
    except Exception:
        pass

    # Update status
    update_project_status(name, "finished")

    return ProjectStatusResponse(
        success=True,
        project_name=name,
        status="finished",
        message=f"Project '{name}' marked as finished"
    )


@router.post("/{name}/archive", response_model=ProjectStatusResponse)
async def archive_project(name: str):
    """
    Archive a project.

    Hides the project from active lists but keeps all data.
    """
    _init_imports()
    funcs = _get_registry_functions()
    get_project_path = funcs[2]
    update_project_status = funcs[5]

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    # Stop any running agents
    from ..services.multi_agent_manager import get_multi_manager
    try:
        manager = await get_multi_manager(name, project_dir)
        await manager.stop_all()
    except Exception:
        pass

    # Update status
    update_project_status(name, "archived")

    return ProjectStatusResponse(
        success=True,
        project_name=name,
        status="archived",
        message=f"Project '{name}' archived"
    )


@router.post("/{name}/restart", response_model=ProjectStatusResponse)
async def restart_project(name: str):
    """
    Restart a project from scratch.

    Clears all features and resets to initial state.
    Use this to start over completely.
    """
    _init_imports()
    funcs = _get_registry_functions()
    get_project_path = funcs[2]
    update_project_status = funcs[5]

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    # Stop any running agents
    from ..services.multi_agent_manager import get_multi_manager
    try:
        manager = await get_multi_manager(name, project_dir)
        await manager.stop_all()
    except Exception:
        pass

    # Delete the features database
    features_db = project_dir / "features.db"
    if features_db.exists():
        features_db.unlink()

    # Update status to active
    update_project_status(name, "active")

    return ProjectStatusResponse(
        success=True,
        project_name=name,
        status="active",
        message=f"Project '{name}' restarted - all features cleared"
    )


@router.post("/{name}/reset", response_model=ProjectStatusResponse)
async def reset_project(name: str):
    """
    Reset project progress but keep features.

    Clears all 'passes' flags so features can be re-worked.
    Use this to retry all features without losing the feature definitions.
    """
    _init_imports()
    funcs = _get_registry_functions()
    get_project_path = funcs[2]
    update_project_status = funcs[5]

    name = validate_project_name(name)
    project_dir = get_project_path(name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    # Stop any running agents
    from ..services.multi_agent_manager import get_multi_manager
    try:
        manager = await get_multi_manager(name, project_dir)
        await manager.stop_all()
    except Exception:
        pass

    # Reset all features to not passing
    features_db = project_dir / "features.db"
    if features_db.exists():
        import sys
        root = Path(__file__).parent.parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

        from api.database import Feature, create_database
        _, SessionLocal = create_database(project_dir)
        session = SessionLocal()
        try:
            session.query(Feature).update({
                Feature.passes: False,
                Feature.in_progress: False,
                Feature.assigned_agent_id: None,
                Feature.attempt_count: 0,
            })
            session.commit()
        finally:
            session.close()

    # Update status to active
    update_project_status(name, "active")

    return ProjectStatusResponse(
        success=True,
        project_name=name,
        status="active",
        message=f"Project '{name}' reset - all features marked as pending"
    )
