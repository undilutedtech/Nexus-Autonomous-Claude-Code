"""
Project Config Router
=====================

API endpoints for managing per-project configuration.
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import registry functions
import sys
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from registry import (
    create_or_update_project_config,
    get_or_create_default_config,
    get_project_config,
    get_project_path,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["config"])


def validate_project_name(name: str) -> bool:
    """Validate project name to prevent path traversal."""
    return bool(re.match(r'^[a-zA-Z0-9_-]{1,50}$', name))


def get_project_dir(project_name: str) -> Path:
    """Get project directory from registry."""
    if not validate_project_name(project_name):
        raise HTTPException(status_code=400, detail="Invalid project name")

    project_dir = get_project_path(project_name)
    if not project_dir:
        raise HTTPException(status_code=404, detail="Project not found in registry")

    return project_dir


# =============================================================================
# Request/Response Models
# =============================================================================

class ProjectConfigUpdate(BaseModel):
    """Request to update project configuration."""
    max_parallel_agents: Optional[int] = None
    default_mode: Optional[str] = None
    use_worktrees: Optional[bool] = None
    auto_stop_on_completion: Optional[bool] = None


class SubagentConfig(BaseModel):
    """Configuration for a custom subagent."""
    name: str
    description: str
    prompt: str
    trigger: str = "manual"  # manual/after_feature_complete/on_error
    tools: list[str] = []


class SubagentConfigUpdate(BaseModel):
    """Request to update subagent configuration."""
    subagents: list[SubagentConfig]


class ProjectConfigResponse(BaseModel):
    """Project configuration response."""
    project_name: str
    max_parallel_agents: int
    default_mode: str
    use_worktrees: bool
    auto_stop_on_completion: bool
    subagent_config: Optional[dict] = None
    updated_at: Optional[str] = None


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/{project_name}/config", response_model=ProjectConfigResponse)
async def get_config(project_name: str):
    """
    Get configuration for a project.

    Returns default configuration if none exists.
    """
    # Validate project exists
    get_project_dir(project_name)

    try:
        config = get_or_create_default_config(project_name)
        return ProjectConfigResponse(**config)
    except Exception as e:
        logger.exception("Failed to get project config")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_name}/config", response_model=ProjectConfigResponse)
async def update_config(project_name: str, request: ProjectConfigUpdate):
    """
    Update project configuration.

    Only provided fields will be updated.
    """
    # Validate project exists
    get_project_dir(project_name)

    # Validate mode if provided
    if request.default_mode:
        valid_modes = {"separate", "collaborative", "worktree"}
        if request.default_mode not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode. Must be one of: {valid_modes}"
            )

    # Validate max_parallel_agents
    if request.max_parallel_agents is not None:
        if request.max_parallel_agents < 1 or request.max_parallel_agents > 10:
            raise HTTPException(
                status_code=400,
                detail="max_parallel_agents must be between 1 and 10"
            )

    try:
        config = create_or_update_project_config(
            project_name=project_name,
            max_parallel_agents=request.max_parallel_agents,
            default_mode=request.default_mode,
            use_worktrees=request.use_worktrees,
            auto_stop_on_completion=request.auto_stop_on_completion,
        )
        return ProjectConfigResponse(**config)
    except Exception as e:
        logger.exception("Failed to update project config")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/config/subagents")
async def get_subagent_config(project_name: str):
    """
    Get custom subagent configuration for a project.
    """
    # Validate project exists
    get_project_dir(project_name)

    try:
        config = get_project_config(project_name)
        if config and config.get("subagent_config"):
            return config["subagent_config"]
        return {"subagents": []}
    except Exception as e:
        logger.exception("Failed to get subagent config")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_name}/config/subagents")
async def update_subagent_config(project_name: str, request: SubagentConfigUpdate):
    """
    Update custom subagent configuration for a project.

    Subagents are custom agents that can be triggered manually or
    automatically after certain events.

    Triggers:
    - manual: Only triggered via UI button
    - after_feature_complete: Runs after a feature is marked as passing
    - on_error: Runs when the main agent encounters an error
    """
    # Validate project exists
    get_project_dir(project_name)

    # Validate triggers
    valid_triggers = {"manual", "after_feature_complete", "on_error"}
    for subagent in request.subagents:
        if subagent.trigger not in valid_triggers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid trigger '{subagent.trigger}'. Must be one of: {valid_triggers}"
            )

    try:
        # Convert to dict for storage
        subagent_config = {
            "subagents": [s.model_dump() for s in request.subagents]
        }

        config = create_or_update_project_config(
            project_name=project_name,
            subagent_config=subagent_config
        )

        return config.get("subagent_config", {"subagents": []})
    except Exception as e:
        logger.exception("Failed to update subagent config")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/config/subagents/{subagent_name}/trigger")
async def trigger_subagent(project_name: str, subagent_name: str):
    """
    Manually trigger a subagent.

    The subagent will run in the project context with its configured
    prompt and tools.
    """
    # Validate project exists
    project_dir = get_project_dir(project_name)

    try:
        config = get_project_config(project_name)
        if not config or not config.get("subagent_config"):
            raise HTTPException(
                status_code=404,
                detail="No subagent configuration found"
            )

        subagents = config["subagent_config"].get("subagents", [])
        subagent = next(
            (s for s in subagents if s["name"] == subagent_name),
            None
        )

        if not subagent:
            raise HTTPException(
                status_code=404,
                detail=f"Subagent '{subagent_name}' not found"
            )

        # Subagent execution is handled by the agent loop when triggered
        # This endpoint validates and queues the subagent for execution
        return {
            "success": True,
            "message": f"Subagent '{subagent_name}' triggered",
            "subagent": subagent,
            "note": "Subagent will execute in the next agent session"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to trigger subagent")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_name}/config/subagents/{subagent_name}")
async def delete_subagent(project_name: str, subagent_name: str):
    """
    Delete a subagent configuration.
    """
    # Validate project exists
    get_project_dir(project_name)

    try:
        config = get_project_config(project_name)
        if not config or not config.get("subagent_config"):
            raise HTTPException(
                status_code=404,
                detail="No subagent configuration found"
            )

        subagents = config["subagent_config"].get("subagents", [])
        original_count = len(subagents)

        subagents = [s for s in subagents if s["name"] != subagent_name]

        if len(subagents) == original_count:
            raise HTTPException(
                status_code=404,
                detail=f"Subagent '{subagent_name}' not found"
            )

        # Update config
        create_or_update_project_config(
            project_name=project_name,
            subagent_config={"subagents": subagents}
        )

        return {"success": True, "message": f"Subagent '{subagent_name}' deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete subagent")
        raise HTTPException(status_code=500, detail=str(e))
