"""
Assets Router
=============

API endpoints for managing project assets (file/image uploads).
"""

import logging
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..services.asset_manager import get_asset_manager

# Import registry for project lookup
import sys
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from registry import get_project_path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["assets"])


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
# Response Models
# =============================================================================

class AssetInfo(BaseModel):
    """Asset information response."""
    filename: str
    path: str
    size: int
    mime_type: Optional[str] = None
    modified_at: Optional[str] = None


class AssetUploadResponse(BaseModel):
    """Response after uploading an asset."""
    success: bool
    filename: str
    original_filename: str
    path: str
    size: int
    mime_type: Optional[str] = None
    spec_reference: str


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/{project_name}/assets", response_model=AssetUploadResponse)
async def upload_asset(
    project_name: str,
    file: UploadFile = File(...),
    overwrite: bool = False
):
    """
    Upload a file to the project's assets directory.

    Supported file types:
    - Images: png, jpg, jpeg, gif, webp, svg, ico
    - Documents: pdf, txt, md, json, xml, yaml
    - Code: py, js, ts, html, css, sql

    Max file size: 10 MB
    """
    project_dir = get_project_dir(project_name)
    manager = get_asset_manager(project_dir)

    try:
        content = await file.read()
        asset_info = manager.upload(
            filename=file.filename,
            content=content,
            overwrite=overwrite
        )

        return AssetUploadResponse(
            success=True,
            filename=asset_info["filename"],
            original_filename=asset_info["original_filename"],
            path=asset_info["path"],
            size=asset_info["size"],
            mime_type=asset_info.get("mime_type"),
            spec_reference=manager.get_spec_reference(asset_info["filename"])
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to upload asset")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/assets")
async def list_assets(project_name: str):
    """
    List all assets for a project.

    Returns assets sorted by modification time (newest first).
    """
    project_dir = get_project_dir(project_name)
    manager = get_asset_manager(project_dir)

    try:
        assets = manager.list_assets()
        total_size = manager.get_total_size()

        return {
            "assets": assets,
            "count": len(assets),
            "total_size": total_size
        }
    except Exception as e:
        logger.exception("Failed to list assets")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/assets/{filename}")
async def get_asset(project_name: str, filename: str):
    """
    Get information about a specific asset.
    """
    project_dir = get_project_dir(project_name)
    manager = get_asset_manager(project_dir)

    try:
        asset = manager.get_asset(filename)
        if asset:
            asset["spec_reference"] = manager.get_spec_reference(filename)
            asset["relative_path"] = manager.get_relative_path(filename)
            return asset
        else:
            raise HTTPException(status_code=404, detail=f"Asset '{filename}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get asset")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/assets/{filename}/download")
async def download_asset(project_name: str, filename: str):
    """
    Download an asset file.
    """
    project_dir = get_project_dir(project_name)
    manager = get_asset_manager(project_dir)

    try:
        asset = manager.get_asset(filename)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset '{filename}' not found")

        return FileResponse(
            path=asset["path"],
            filename=filename,
            media_type=asset.get("mime_type", "application/octet-stream")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to download asset")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_name}/assets/{filename}")
async def delete_asset(project_name: str, filename: str):
    """
    Delete an asset.
    """
    project_dir = get_project_dir(project_name)
    manager = get_asset_manager(project_dir)

    try:
        success = manager.delete_asset(filename)

        if success:
            return {"success": True, "message": f"Asset '{filename}' deleted"}
        else:
            raise HTTPException(status_code=404, detail=f"Asset '{filename}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete asset")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/assets-stats")
async def get_assets_stats(project_name: str):
    """
    Get statistics about project assets.
    """
    project_dir = get_project_dir(project_name)
    manager = get_asset_manager(project_dir)

    try:
        assets = manager.list_assets()
        total_size = manager.get_total_size()

        # Group by mime type
        by_type = {}
        for asset in assets:
            mime = asset.get("mime_type") or "unknown"
            if mime not in by_type:
                by_type[mime] = {"count": 0, "size": 0}
            by_type[mime]["count"] += 1
            by_type[mime]["size"] += asset["size"]

        return {
            "total_count": len(assets),
            "total_size": total_size,
            "by_type": by_type
        }
    except Exception as e:
        logger.exception("Failed to get assets stats")
        raise HTTPException(status_code=500, detail=str(e))
