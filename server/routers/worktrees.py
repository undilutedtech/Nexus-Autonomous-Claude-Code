"""
Git Worktrees Router
====================

API endpoints for managing git worktrees for parallel agents.
"""

import logging
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.worktree_manager import get_worktree_manager

# Import registry for project lookup
import sys
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from registry import get_project_path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["worktrees"])


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

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    return project_dir


# =============================================================================
# Request/Response Models
# =============================================================================

class CreateWorktreeRequest(BaseModel):
    """Request to create a new worktree."""
    agent_id: str
    branch: Optional[str] = None


class MergeWorktreeRequest(BaseModel):
    """Request to merge a worktree."""
    target_branch: str = "main"


class WorktreeResponse(BaseModel):
    """Worktree information response."""
    agent_id: str
    path: str
    branch: Optional[str] = None
    has_changes: bool = False


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/{project_name}/worktrees")
async def create_worktree(project_name: str, request: CreateWorktreeRequest):
    """
    Create a new git worktree for an agent.

    Initializes git repository if needed and creates a worktree
    with a dedicated branch for the agent.
    """
    project_dir = get_project_dir(project_name)
    manager = get_worktree_manager(project_dir)

    try:
        worktree_path = await manager.create_worktree(
            agent_id=request.agent_id,
            branch=request.branch
        )

        if worktree_path:
            return {
                "success": True,
                "agent_id": request.agent_id,
                "path": str(worktree_path),
                "branch": request.branch or f"agent/{request.agent_id}",
                "message": f"Worktree created at {worktree_path}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create worktree")
    except Exception as e:
        logger.exception("Failed to create worktree")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/worktrees")
async def list_worktrees(project_name: str):
    """
    List all worktrees for a project.
    """
    project_dir = get_project_dir(project_name)
    manager = get_worktree_manager(project_dir)

    try:
        worktrees = await manager.list_worktrees()
        return {"worktrees": worktrees}
    except Exception as e:
        logger.exception("Failed to list worktrees")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/worktrees/{agent_id}")
async def get_worktree_status(project_name: str, agent_id: str):
    """
    Get status of a specific worktree.
    """
    project_dir = get_project_dir(project_name)
    manager = get_worktree_manager(project_dir)

    try:
        status = await manager.get_worktree_status(agent_id)
        if status:
            return status
        else:
            raise HTTPException(status_code=404, detail=f"Worktree for {agent_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get worktree status")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/worktrees/{agent_id}/merge")
async def merge_worktree(project_name: str, agent_id: str, request: MergeWorktreeRequest):
    """
    Merge changes from a worktree branch into the target branch.
    """
    project_dir = get_project_dir(project_name)
    manager = get_worktree_manager(project_dir)

    try:
        success, message = await manager.merge_worktree(
            agent_id=agent_id,
            target_branch=request.target_branch
        )

        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=409, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to merge worktree")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_name}/worktrees/{agent_id}")
async def delete_worktree(project_name: str, agent_id: str):
    """
    Remove a worktree for an agent.
    """
    project_dir = get_project_dir(project_name)
    manager = get_worktree_manager(project_dir)

    try:
        success = await manager.cleanup_worktree(agent_id)

        if success:
            return {"success": True, "message": f"Worktree for {agent_id} removed"}
        else:
            raise HTTPException(status_code=500, detail="Failed to remove worktree")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete worktree")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/worktrees/sync")
async def sync_worktrees(project_name: str, target_branch: str = "main"):
    """
    Sync all worktrees with the latest changes from target branch.
    """
    project_dir = get_project_dir(project_name)
    manager = get_worktree_manager(project_dir)

    try:
        results = await manager.sync_worktrees(target_branch)
        return {"results": results}
    except Exception as e:
        logger.exception("Failed to sync worktrees")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/worktrees/init")
async def init_repository(project_name: str):
    """
    Initialize a git repository for the project.

    Required before creating worktrees.
    """
    project_dir = get_project_dir(project_name)
    manager = get_worktree_manager(project_dir)

    try:
        success = await manager.init_repository()

        if success:
            return {
                "success": True,
                "is_git_repo": manager.is_git_repo(),
                "message": "Repository initialized"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize repository")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to initialize repository")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/worktrees/is-git-repo")
async def check_is_git_repo(project_name: str):
    """
    Check if the project is a git repository.
    """
    project_dir = get_project_dir(project_name)
    manager = get_worktree_manager(project_dir)

    return {"is_git_repo": manager.is_git_repo()}
