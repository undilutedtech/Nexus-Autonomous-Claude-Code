"""
Multi-Agent Router
==================

API endpoints for managing multiple parallel agents on a project.
"""

import logging
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.multi_agent_manager import get_multi_manager, remove_multi_manager

# Import registry for project lookup
import sys
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from registry import get_project_path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["agents"])


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

class SpawnAgentRequest(BaseModel):
    """Request to spawn a new agent."""
    mode: str = "separate"  # separate/collaborative/worktree
    worktree_path: Optional[str] = None


class StartAgentRequest(BaseModel):
    """Request to start an agent."""
    yolo_mode: bool = False
    model: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent information response."""
    agent_id: str
    project_name: str
    status: str
    mode: str
    pid: Optional[int] = None
    started_at: Optional[str] = None
    current_feature_id: Optional[int] = None
    worktree_path: Optional[str] = None


class AgentActionResponse(BaseModel):
    """Response for agent actions."""
    success: bool
    agent_id: str
    status: str
    message: str


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/{project_name}/agents", response_model=AgentResponse)
async def spawn_agent(project_name: str, request: SpawnAgentRequest):
    """
    Spawn a new agent for a project.

    Creates a new agent instance that can be started independently.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        agent_info = await manager.spawn_agent(
            mode=request.mode,
            worktree_path=request.worktree_path
        )

        return AgentResponse(
            agent_id=agent_info["agent_id"],
            project_name=project_name,
            status=agent_info["status"],
            mode=agent_info["mode"],
            worktree_path=agent_info.get("worktree_path"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to spawn agent")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/agents")
async def list_agents(project_name: str):
    """
    List all agents for a project.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        agents = manager.get_all_agent_statuses()

        return {"agents": agents}
    except Exception as e:
        logger.exception("Failed to list agents")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/agents/{agent_id}/status")
async def get_agent_status(project_name: str, agent_id: str):
    """
    Get status of a specific agent.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        status = manager.get_agent_status(agent_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to get agent status")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/agents/{agent_id}/start", response_model=AgentActionResponse)
async def start_agent(project_name: str, agent_id: str, request: StartAgentRequest):
    """
    Start a specific agent.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        result = await manager.start_agent(
            agent_id=agent_id,
            yolo_mode=request.yolo_mode,
            model=request.model
        )

        return AgentActionResponse(
            success=result.get("success", True),
            agent_id=agent_id,
            status=result.get("status", "running"),
            message=result.get("message", f"Agent {agent_id} started")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to start agent")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/agents/{agent_id}/stop", response_model=AgentActionResponse)
async def stop_agent(project_name: str, agent_id: str):
    """
    Stop a specific agent.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        result = await manager.stop_agent(agent_id)

        return AgentActionResponse(
            success=result.get("success", True),
            agent_id=agent_id,
            status="stopped",
            message=result.get("message", f"Agent {agent_id} stopped")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to stop agent")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/agents/{agent_id}/pause", response_model=AgentActionResponse)
async def pause_agent(project_name: str, agent_id: str):
    """
    Pause a specific agent.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        result = await manager.pause_agent(agent_id)

        return AgentActionResponse(
            success=result.get("success", True),
            agent_id=agent_id,
            status="paused",
            message=result.get("message", f"Agent {agent_id} paused")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to pause agent")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/agents/{agent_id}/resume", response_model=AgentActionResponse)
async def resume_agent(project_name: str, agent_id: str):
    """
    Resume a paused agent.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        result = await manager.resume_agent(agent_id)

        return AgentActionResponse(
            success=result.get("success", True),
            agent_id=agent_id,
            status="running",
            message=result.get("message", f"Agent {agent_id} resumed")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to resume agent")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_name}/agents/{agent_id}")
async def remove_agent(project_name: str, agent_id: str):
    """
    Remove an agent from a project.

    Stops the agent if running and removes from registry.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        success = await manager.remove_agent(agent_id)

        if success:
            return {"success": True, "message": f"Agent {agent_id} removed"}
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to remove agent")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_name}/agents/stop-all")
async def stop_all_agents(project_name: str):
    """
    Stop all agents for a project.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        await manager.stop_all()

        return {"success": True, "message": "All agents stopped"}
    except Exception as e:
        logger.exception("Failed to stop all agents")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/agents/locked-features")
async def get_locked_features(project_name: str):
    """
    Get all features currently locked by agents.
    """
    project_dir = get_project_dir(project_name)

    try:
        manager = await get_multi_manager(project_name, project_dir)
        locks = manager.get_locked_features()

        return {"locked_features": locks}
    except Exception as e:
        logger.exception("Failed to get locked features")
        raise HTTPException(status_code=500, detail=str(e))
