"""
Asset Manager Service
=====================

Handles file and image uploads for projects.
Provides upload, listing, and deletion of project assets.
"""

import hashlib
import logging
import mimetypes
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Optional

logger = logging.getLogger(__name__)


class AssetManager:
    """
    Manages file and image assets for a project.

    Assets are stored in the project's assets/ directory and can be
    referenced in the app specification and prompts.
    """

    # Allowed file types for upload
    ALLOWED_EXTENSIONS = {
        # Images
        'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico',
        # Documents
        'pdf', 'txt', 'md', 'json', 'xml', 'yaml', 'yml',
        # Code samples
        'py', 'js', 'ts', 'html', 'css', 'sql',
    }

    ALLOWED_MIME_TYPES = {
        # Images
        'image/png', 'image/jpeg', 'image/gif', 'image/webp',
        'image/svg+xml', 'image/x-icon',
        # Documents
        'application/pdf', 'text/plain', 'text/markdown',
        'application/json', 'application/xml', 'text/xml',
        'application/x-yaml', 'text/yaml',
        # Code
        'text/x-python', 'application/javascript', 'text/javascript',
        'text/typescript', 'text/html', 'text/css',
    }

    # Maximum file size (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir.resolve()
        self.assets_dir = self.project_dir / "assets"

        # Ensure assets directory exists
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def _validate_filename(self, filename: str) -> tuple[bool, str]:
        """
        Validate a filename for security.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for empty filename
        if not filename:
            return False, "Filename cannot be empty"

        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return False, "Invalid filename: path traversal not allowed"

        # Check extension
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File type '{ext}' not allowed"

        return True, ""

    def _get_safe_filename(self, filename: str) -> str:
        """
        Generate a safe, unique filename.

        Preserves the original extension but sanitizes the name.
        """
        # Get extension
        if "." in filename:
            name, ext = filename.rsplit(".", 1)
            ext = ext.lower()
        else:
            name, ext = filename, ""

        # Sanitize name (keep alphanumeric, dash, underscore)
        safe_name = "".join(
            c if c.isalnum() or c in "-_" else "_"
            for c in name
        )

        # Limit length
        safe_name = safe_name[:50]

        if ext:
            return f"{safe_name}.{ext}"
        return safe_name

    def upload(
        self,
        filename: str,
        content: bytes,
        overwrite: bool = False
    ) -> dict[str, Any]:
        """
        Upload a file to the assets directory.

        Args:
            filename: Original filename
            content: File content as bytes
            overwrite: Whether to overwrite existing file

        Returns:
            Asset info dictionary

        Raises:
            ValueError: If file validation fails
        """
        # Validate filename
        is_valid, error = self._validate_filename(filename)
        if not is_valid:
            raise ValueError(error)

        # Check file size
        if len(content) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {len(content)} bytes "
                f"(max: {self.MAX_FILE_SIZE} bytes)"
            )

        # Check mime type
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type and mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(f"MIME type '{mime_type}' not allowed")

        # Generate safe filename
        safe_filename = self._get_safe_filename(filename)
        file_path = self.assets_dir / safe_filename

        # Handle existing file
        if file_path.exists() and not overwrite:
            # Add timestamp to make unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if "." in safe_filename:
                name, ext = safe_filename.rsplit(".", 1)
                safe_filename = f"{name}_{timestamp}.{ext}"
            else:
                safe_filename = f"{safe_filename}_{timestamp}"
            file_path = self.assets_dir / safe_filename

        # Write file
        file_path.write_bytes(content)

        # Calculate hash for integrity (SHA256 for security compliance)
        file_hash = hashlib.sha256(content).hexdigest()

        logger.info("Uploaded asset: %s (%d bytes)", safe_filename, len(content))

        return {
            "filename": safe_filename,
            "original_filename": filename,
            "path": str(file_path),
            "size": len(content),
            "mime_type": mime_type,
            "hash": file_hash,
            "uploaded_at": datetime.now().isoformat(),
        }

    def upload_stream(
        self,
        filename: str,
        stream: BinaryIO,
        overwrite: bool = False
    ) -> dict[str, Any]:
        """
        Upload a file from a stream.

        Args:
            filename: Original filename
            stream: File stream
            overwrite: Whether to overwrite existing file

        Returns:
            Asset info dictionary
        """
        content = stream.read()
        return self.upload(filename, content, overwrite)

    def list_assets(self) -> list[dict[str, Any]]:
        """
        List all assets in the project.

        Returns:
            List of asset info dictionaries
        """
        assets = []

        if not self.assets_dir.exists():
            return assets

        for file_path in self.assets_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                mime_type, _ = mimetypes.guess_type(file_path.name)

                assets.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "mime_type": mime_type,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })

        # Sort by modification time (newest first)
        assets.sort(key=lambda a: a["modified_at"], reverse=True)

        return assets

    def get_asset(self, filename: str) -> Optional[dict[str, Any]]:
        """
        Get information about a specific asset.

        Args:
            filename: The asset filename

        Returns:
            Asset info dictionary, or None if not found
        """
        # Validate to prevent path traversal
        is_valid, _ = self._validate_filename(filename)
        if not is_valid:
            return None

        file_path = self.assets_dir / filename

        if not file_path.exists() or not file_path.is_file():
            return None

        stat = file_path.stat()
        mime_type, _ = mimetypes.guess_type(filename)

        return {
            "filename": filename,
            "path": str(file_path),
            "size": stat.st_size,
            "mime_type": mime_type,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    def get_asset_content(self, filename: str) -> Optional[bytes]:
        """
        Get the content of an asset.

        Args:
            filename: The asset filename

        Returns:
            File content as bytes, or None if not found
        """
        is_valid, _ = self._validate_filename(filename)
        if not is_valid:
            return None

        file_path = self.assets_dir / filename

        if not file_path.exists() or not file_path.is_file():
            return None

        return file_path.read_bytes()

    def delete_asset(self, filename: str) -> bool:
        """
        Delete an asset.

        Args:
            filename: The asset filename

        Returns:
            True if deleted, False if not found
        """
        is_valid, _ = self._validate_filename(filename)
        if not is_valid:
            return False

        file_path = self.assets_dir / filename

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            logger.info("Deleted asset: %s", filename)
            return True
        except Exception as e:
            logger.error("Failed to delete asset %s: %s", filename, e)
            return False

    def get_spec_reference(self, filename: str) -> str:
        """
        Generate a reference string for use in app_spec.txt.

        Args:
            filename: The asset filename

        Returns:
            Reference string like "[See: assets/image.png]"
        """
        return f"[See: assets/{filename}]"

    def get_relative_path(self, filename: str) -> str:
        """
        Get the path relative to the project directory.

        Args:
            filename: The asset filename

        Returns:
            Relative path like "assets/image.png"
        """
        return f"assets/{filename}"

    def cleanup_orphaned_assets(self, referenced_files: set[str]) -> list[str]:
        """
        Remove assets that are not referenced anywhere.

        Args:
            referenced_files: Set of filenames that are referenced

        Returns:
            List of deleted filenames
        """
        deleted = []

        for asset in self.list_assets():
            filename = asset["filename"]
            if filename not in referenced_files:
                if self.delete_asset(filename):
                    deleted.append(filename)

        return deleted

    def get_total_size(self) -> int:
        """
        Get the total size of all assets.

        Returns:
            Total size in bytes
        """
        total = 0
        for asset in self.list_assets():
            total += asset["size"]
        return total


# Cache of asset managers per project
_asset_managers: dict[str, AssetManager] = {}


def get_asset_manager(project_dir: Path) -> AssetManager:
    """Get or create an AssetManager for a project."""
    key = str(project_dir.resolve())
    if key not in _asset_managers:
        _asset_managers[key] = AssetManager(project_dir)
    return _asset_managers[key]
