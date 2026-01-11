"""
Features Router
===============

API endpoints for feature/test case management.
"""

import logging
import re
from contextlib import contextmanager
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..schemas import (
    FeatureCreate,
    FeatureListResponse,
    FeatureResponse,
)

# Lazy imports to avoid circular dependencies
_create_database = None
_Feature = None

logger = logging.getLogger(__name__)


def _get_project_path(project_name: str) -> Path:
    """Get project path from registry."""
    import sys
    root = Path(__file__).parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from registry import get_project_path
    return get_project_path(project_name)


def _get_db_classes():
    """Lazy import of database classes."""
    global _create_database, _Feature
    if _create_database is None:
        import sys
        from pathlib import Path
        root = Path(__file__).parent.parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from api.database import Feature, create_database
        _create_database = create_database
        _Feature = Feature
    return _create_database, _Feature


router = APIRouter(prefix="/api/projects/{project_name}/features", tags=["features"])


def validate_project_name(name: str) -> str:
    """Validate and sanitize project name to prevent path traversal."""
    if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', name):
        raise HTTPException(
            status_code=400,
            detail="Invalid project name"
        )
    return name


@contextmanager
def get_db_session(project_dir: Path):
    """
    Context manager for database sessions.
    Ensures session is always closed, even on exceptions.
    """
    create_database, _ = _get_db_classes()
    _, SessionLocal = create_database(project_dir)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def feature_to_response(f) -> FeatureResponse:
    """Convert a Feature model to a FeatureResponse."""
    return FeatureResponse(
        id=f.id,
        priority=f.priority,
        category=f.category,
        name=f.name,
        description=f.description,
        steps=f.steps if isinstance(f.steps, list) else [],
        passes=f.passes,
        in_progress=f.in_progress,
    )


@router.get("", response_model=FeatureListResponse)
async def list_features(project_name: str):
    """
    List all features for a project organized by status.

    Returns features in three lists:
    - pending: passes=False, not currently being worked on
    - in_progress: features currently being worked on (tracked via agent output)
    - done: passes=True
    """
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    db_file = project_dir / "features.db"
    if not db_file.exists():
        return FeatureListResponse(pending=[], in_progress=[], done=[])

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            all_features = session.query(Feature).order_by(Feature.priority).all()

            pending = []
            in_progress = []
            done = []

            for f in all_features:
                feature_response = feature_to_response(f)
                if f.passes:
                    done.append(feature_response)
                elif f.in_progress:
                    in_progress.append(feature_response)
                else:
                    pending.append(feature_response)

            return FeatureListResponse(
                pending=pending,
                in_progress=in_progress,
                done=done,
            )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Database error in list_features")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.post("", response_model=FeatureResponse)
async def create_feature(project_name: str, feature: FeatureCreate):
    """Create a new feature/test case manually."""
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            # Get next priority if not specified
            if feature.priority is None:
                max_priority = session.query(Feature).order_by(Feature.priority.desc()).first()
                priority = (max_priority.priority + 1) if max_priority else 1
            else:
                priority = feature.priority

            # Create new feature
            db_feature = Feature(
                priority=priority,
                category=feature.category,
                name=feature.name,
                description=feature.description,
                steps=feature.steps,
                passes=False,
            )

            session.add(db_feature)
            session.commit()
            session.refresh(db_feature)

            return feature_to_response(db_feature)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create feature")
        raise HTTPException(status_code=500, detail="Failed to create feature")


@router.get("/{feature_id}", response_model=FeatureResponse)
async def get_feature(project_name: str, feature_id: int):
    """Get details of a specific feature."""
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    db_file = project_dir / "features.db"
    if not db_file.exists():
        raise HTTPException(status_code=404, detail="No features database found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            feature = session.query(Feature).filter(Feature.id == feature_id).first()

            if not feature:
                raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

            return feature_to_response(feature)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Database error in get_feature")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.delete("/{feature_id}")
async def delete_feature(project_name: str, feature_id: int):
    """Delete a feature."""
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            feature = session.query(Feature).filter(Feature.id == feature_id).first()

            if not feature:
                raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

            session.delete(feature)
            session.commit()

            return {"success": True, "message": f"Feature {feature_id} deleted"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to delete feature")
        raise HTTPException(status_code=500, detail="Failed to delete feature")


@router.patch("/{feature_id}/skip")
async def skip_feature(project_name: str, feature_id: int):
    """
    Mark a feature as skipped by moving it to the end of the priority queue.

    This doesn't delete the feature but gives it a very high priority number
    so it will be processed last.
    """
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            feature = session.query(Feature).filter(Feature.id == feature_id).first()

            if not feature:
                raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

            # Set priority to max + 1000 to push to end
            max_priority = session.query(Feature).order_by(Feature.priority.desc()).first()
            feature.priority = (max_priority.priority if max_priority else 0) + 1000
            feature.in_progress = False  # Also clear in_progress when skipping

            session.commit()

            return {"success": True, "message": f"Feature {feature_id} moved to end of queue"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to skip feature")
        raise HTTPException(status_code=500, detail="Failed to skip feature")


@router.patch("/{feature_id}/clear-in-progress")
async def clear_in_progress(project_name: str, feature_id: int):
    """
    Clear the in-progress status of a feature.

    Use this when a feature is stuck in "in_progress" status after the agent
    crashed or was stopped. This returns the feature to the pending queue.
    """
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            feature = session.query(Feature).filter(Feature.id == feature_id).first()

            if not feature:
                raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

            if not feature.in_progress:
                return {"success": True, "message": f"Feature {feature_id} was not in progress"}

            feature.in_progress = False
            session.commit()

            return {"success": True, "message": f"Feature {feature_id} in-progress status cleared"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to clear in-progress status")
        raise HTTPException(status_code=500, detail="Failed to clear in-progress status")


# =============================================================================
# Enhanced Feature Management Endpoints
# =============================================================================

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BulkFeatureCreate(BaseModel):
    """Request to create multiple features at once."""
    features: list[FeatureCreate]


class FeatureAssignRequest(BaseModel):
    """Request to assign a feature to an agent."""
    agent_id: str


@router.post("/bulk", response_model=list[FeatureResponse])
async def bulk_create_features(project_name: str, request: BulkFeatureCreate):
    """
    Create multiple features at once.

    Useful for adding a batch of new requirements to an ongoing project.
    """
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            # Get the current max priority
            max_priority_feature = session.query(Feature).order_by(Feature.priority.desc()).first()
            next_priority = (max_priority_feature.priority + 1) if max_priority_feature else 1

            created_features = []

            for feat in request.features:
                priority = feat.priority if feat.priority is not None else next_priority
                next_priority = max(next_priority, priority) + 1

                db_feature = Feature(
                    priority=priority,
                    category=feat.category,
                    name=feat.name,
                    description=feat.description,
                    steps=feat.steps,
                    passes=False,
                    source="manual",
                    added_at=datetime.now(),
                )

                session.add(db_feature)
                session.flush()  # Get the ID
                created_features.append(feature_to_response(db_feature))

            session.commit()
            return created_features
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to bulk create features")
        raise HTTPException(status_code=500, detail="Failed to bulk create features")


@router.patch("/{feature_id}/assign")
async def assign_feature(project_name: str, feature_id: int, request: FeatureAssignRequest):
    """
    Assign a feature to a specific agent.

    This locks the feature so only the assigned agent can work on it.
    """
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            feature = session.query(Feature).filter(Feature.id == feature_id).first()

            if not feature:
                raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

            if feature.passes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Feature {feature_id} is already complete"
                )

            feature.assigned_agent_id = request.agent_id
            session.commit()

            return {
                "success": True,
                "message": f"Feature {feature_id} assigned to {request.agent_id}",
                "feature": feature_to_response(feature)
            }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to assign feature")
        raise HTTPException(status_code=500, detail="Failed to assign feature")


@router.patch("/{feature_id}/unassign")
async def unassign_feature(project_name: str, feature_id: int):
    """
    Remove agent assignment from a feature.

    The feature will be available for any agent to pick up.
    """
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            feature = session.query(Feature).filter(Feature.id == feature_id).first()

            if not feature:
                raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

            feature.assigned_agent_id = None
            session.commit()

            return {
                "success": True,
                "message": f"Feature {feature_id} unassigned",
                "feature": feature_to_response(feature)
            }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to unassign feature")
        raise HTTPException(status_code=500, detail="Failed to unassign feature")


@router.patch("/{feature_id}/requeue")
async def requeue_feature(project_name: str, feature_id: int):
    """
    Requeue a feature to be worked on again.

    Clears the passes flag and any assignment, moving it back to pending.
    Useful when a previously "done" feature needs to be reworked.
    """
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            feature = session.query(Feature).filter(Feature.id == feature_id).first()

            if not feature:
                raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

            feature.passes = False
            feature.in_progress = False
            feature.assigned_agent_id = None
            # Increment attempt count
            feature.attempt_count = (feature.attempt_count or 0) + 1
            session.commit()

            return {
                "success": True,
                "message": f"Feature {feature_id} requeued for rework",
                "feature": feature_to_response(feature)
            }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to requeue feature")
        raise HTTPException(status_code=500, detail="Failed to requeue feature")


@router.patch("/{feature_id}/update")
async def update_feature(project_name: str, feature_id: int, update: FeatureCreate):
    """
    Update a feature's details.

    Can update category, name, description, and steps.
    """
    project_name = validate_project_name(project_name)
    project_dir = _get_project_path(project_name)

    if not project_dir:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in registry")

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")

    _, Feature = _get_db_classes()

    try:
        with get_db_session(project_dir) as session:
            feature = session.query(Feature).filter(Feature.id == feature_id).first()

            if not feature:
                raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")

            if update.category:
                feature.category = update.category
            if update.name:
                feature.name = update.name
            if update.description:
                feature.description = update.description
            if update.steps:
                feature.steps = update.steps
            if update.priority is not None:
                feature.priority = update.priority

            session.commit()

            return {
                "success": True,
                "message": f"Feature {feature_id} updated",
                "feature": feature_to_response(feature)
            }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to update feature")
        raise HTTPException(status_code=500, detail="Failed to update feature")
