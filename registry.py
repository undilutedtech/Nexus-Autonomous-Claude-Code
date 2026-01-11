"""
Project Registry Module
=======================

Cross-platform project registry for storing project name to path mappings.
Uses SQLite database stored at ~/.nexus/registry.db.
"""

import logging
import os
import re
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import JSON

# Module logger
logger = logging.getLogger(__name__)


# =============================================================================
# Model Configuration (Single Source of Truth)
# =============================================================================

# Available models with display names
# To add a new model: add an entry here with {"id": "model-id", "name": "Display Name"}
AVAILABLE_MODELS = [
    {"id": "claude-opus-4-5-20251101", "name": "Claude Opus 4.5"},
    {"id": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet 4.5"},
]

# List of valid model IDs (derived from AVAILABLE_MODELS)
VALID_MODELS = [m["id"] for m in AVAILABLE_MODELS]

# Default model and settings
DEFAULT_MODEL = "claude-opus-4-5-20251101"
DEFAULT_YOLO_MODE = False

# SQLite connection settings
SQLITE_TIMEOUT = 30  # seconds to wait for database lock
SQLITE_MAX_RETRIES = 3  # number of retry attempts on busy database


# =============================================================================
# Exceptions
# =============================================================================

class RegistryError(Exception):
    """Base registry exception."""
    pass


class RegistryNotFound(RegistryError):
    """Registry file doesn't exist."""
    pass


class RegistryCorrupted(RegistryError):
    """Registry database is corrupted."""
    pass


class RegistryPermissionDenied(RegistryError):
    """Can't read/write registry file."""
    pass


# =============================================================================
# SQLAlchemy Model
# =============================================================================

Base = declarative_base()


class Project(Base):
    """SQLAlchemy model for registered projects."""
    __tablename__ = "projects"

    name = Column(String(50), primary_key=True, index=True)
    path = Column(String, nullable=False)  # POSIX format for cross-platform
    created_at = Column(DateTime, nullable=False)
    # New columns for lifecycle management
    status = Column(String(20), default="active", index=True)  # active/paused/finished/archived
    last_agent_run = Column(DateTime, nullable=True)
    completion_percentage = Column(Float, default=0.0)


class ProjectAgent(Base):
    """SQLAlchemy model for tracking multiple agents per project."""
    __tablename__ = "project_agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(50), ForeignKey("projects.name"), nullable=False, index=True)
    agent_id = Column(String(50), nullable=False)  # e.g., "agent-1", "agent-2"
    worktree_path = Column(String, nullable=True)  # Path to git worktree if used
    status = Column(String(20), default="stopped")  # stopped/running/paused/crashed
    current_feature_id = Column(Integer, nullable=True)  # Feature being worked on
    pid = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=True)
    mode = Column(String(20), default="separate")  # separate/collaborative/worktree
    created_at = Column(DateTime, nullable=False)


class ProjectConfig(Base):
    """SQLAlchemy model for per-project configuration."""
    __tablename__ = "project_config"

    project_name = Column(String(50), ForeignKey("projects.name"), primary_key=True)
    max_parallel_agents = Column(Integer, default=1)
    default_mode = Column(String(20), default="separate")  # separate/collaborative/worktree
    use_worktrees = Column(Boolean, default=False)
    auto_stop_on_completion = Column(Boolean, default=True)
    subagent_config = Column(JSON, nullable=True)  # Custom subagent configuration
    updated_at = Column(DateTime, nullable=False)


class Settings(Base):
    """SQLAlchemy model for global settings (key-value store)."""
    __tablename__ = "settings"

    key = Column(String(50), primary_key=True)
    value = Column(String(500), nullable=False)
    updated_at = Column(DateTime, nullable=False)


# =============================================================================
# Database Connection
# =============================================================================

# Module-level singleton for database engine with thread-safe initialization
_engine = None
_SessionLocal = None
_engine_lock = threading.Lock()


def get_config_dir() -> Path:
    """
    Get the config directory: ~/.nexus/

    Returns:
        Path to ~/.nexus/ (created if it doesn't exist)
    """
    config_dir = Path.home() / ".nexus"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_registry_path() -> Path:
    """Get the path to the registry database."""
    return get_config_dir() / "registry.db"


def _get_engine():
    """
    Get or create the database engine (thread-safe singleton pattern).

    Returns:
        Tuple of (engine, SessionLocal)
    """
    global _engine, _SessionLocal

    # Double-checked locking for thread safety
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                db_path = get_registry_path()
                db_url = f"sqlite:///{db_path.as_posix()}"
                _engine = create_engine(
                    db_url,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": SQLITE_TIMEOUT,
                    }
                )
                Base.metadata.create_all(bind=_engine)
                _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
                logger.debug("Initialized registry database at: %s", db_path)

    return _engine, _SessionLocal


@contextmanager
def _get_session():
    """
    Context manager for database sessions with automatic commit/rollback.

    Includes retry logic for SQLite busy database errors.

    Yields:
        SQLAlchemy session
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _with_retry(func, *args, **kwargs):
    """
    Execute a database operation with retry logic for busy database.

    Args:
        func: Function to execute
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Result of the function

    Raises:
        Last exception if all retries fail
    """
    last_error = None
    for attempt in range(SQLITE_MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            if "database is locked" in error_str or "sqlite_busy" in error_str:
                if attempt < SQLITE_MAX_RETRIES - 1:
                    wait_time = (2 ** attempt) * 0.1  # Exponential backoff: 0.1s, 0.2s, 0.4s
                    logger.warning(
                        "Database busy, retrying in %.1fs (attempt %d/%d)",
                        wait_time, attempt + 1, SQLITE_MAX_RETRIES
                    )
                    time.sleep(wait_time)
                    continue
            raise
    raise last_error


# =============================================================================
# Project CRUD Functions
# =============================================================================

def register_project(name: str, path: Path) -> None:
    """
    Register a new project in the registry.

    Args:
        name: The project name (unique identifier).
        path: The absolute path to the project directory.

    Raises:
        ValueError: If project name is invalid or path is not absolute.
        RegistryError: If a project with that name already exists.
    """
    # Validate name
    if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', name):
        raise ValueError(
            "Invalid project name. Use only letters, numbers, hyphens, "
            "and underscores (1-50 chars)."
        )

    # Ensure path is absolute
    path = Path(path).resolve()

    with _get_session() as session:
        existing = session.query(Project).filter(Project.name == name).first()
        if existing:
            # Check if the existing path still exists
            existing_path = Path(existing.path)
            if not existing_path.exists():
                # Old path is gone - update to new path
                logger.info(
                    "Project '%s' old path no longer exists (%s), updating to new path: %s",
                    name, existing.path, path
                )
                existing.path = path.as_posix()
                existing.status = "active"  # Reset status for relocated project
                return
            else:
                logger.warning("Attempted to register duplicate project: %s", name)
                raise RegistryError(
                    f"Project '{name}' already exists at {existing.path}"
                )

        project = Project(
            name=name,
            path=path.as_posix(),
            created_at=datetime.now()
        )
        session.add(project)

    logger.info("Registered project '%s' at path: %s", name, path)


def unregister_project(name: str) -> bool:
    """
    Remove a project from the registry.

    Args:
        name: The project name to remove.

    Returns:
        True if removed, False if project wasn't found.
    """
    with _get_session() as session:
        project = session.query(Project).filter(Project.name == name).first()
        if not project:
            logger.debug("Attempted to unregister non-existent project: %s", name)
            return False

        session.delete(project)

    logger.info("Unregistered project: %s", name)
    return True


def get_project_path(name: str) -> Path | None:
    """
    Look up a project's path by name.

    Args:
        name: The project name.

    Returns:
        The project Path, or None if not found.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        project = session.query(Project).filter(Project.name == name).first()
        if project is None:
            return None
        return Path(project.path)
    finally:
        session.close()


def list_registered_projects() -> dict[str, dict[str, Any]]:
    """
    Get all registered projects.

    Returns:
        Dictionary mapping project names to their info dictionaries.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        projects = session.query(Project).all()
        return {
            p.name: {
                "path": p.path,
                "status": p.status or "active",
                "completion_percentage": p.completion_percentage or 0.0,
                "last_agent_run": p.last_agent_run.isoformat() if p.last_agent_run else None,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in projects
        }
    finally:
        session.close()


def get_project_info(name: str) -> dict[str, Any] | None:
    """
    Get full info about a project.

    Args:
        name: The project name.

    Returns:
        Project info dictionary, or None if not found.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        project = session.query(Project).filter(Project.name == name).first()
        if project is None:
            return None
        return {
            "path": project.path,
            "created_at": project.created_at.isoformat() if project.created_at else None
        }
    finally:
        session.close()


def update_project_path(name: str, new_path: Path) -> bool:
    """
    Update a project's path (for relocating projects).

    Args:
        name: The project name.
        new_path: The new absolute path.

    Returns:
        True if updated, False if project wasn't found.
    """
    new_path = Path(new_path).resolve()

    with _get_session() as session:
        project = session.query(Project).filter(Project.name == name).first()
        if not project:
            return False

        project.path = new_path.as_posix()

    return True


# =============================================================================
# Validation Functions
# =============================================================================

def validate_project_path(path: Path) -> tuple[bool, str]:
    """
    Validate that a project path is accessible and writable.

    Args:
        path: The path to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    path = Path(path).resolve()

    # Check if path exists
    if not path.exists():
        return False, f"Path does not exist: {path}"

    # Check if it's a directory
    if not path.is_dir():
        return False, f"Path is not a directory: {path}"

    # Check read permissions
    if not os.access(path, os.R_OK):
        return False, f"No read permission: {path}"

    # Check write permissions
    if not os.access(path, os.W_OK):
        return False, f"No write permission: {path}"

    return True, ""


def cleanup_stale_projects() -> list[str]:
    """
    Remove projects from registry whose paths no longer exist.

    Returns:
        List of removed project names.
    """
    removed = []

    with _get_session() as session:
        projects = session.query(Project).all()
        for project in projects:
            path = Path(project.path)
            if not path.exists():
                session.delete(project)
                removed.append(project.name)

    if removed:
        logger.info("Cleaned up stale projects: %s", removed)

    return removed


def list_valid_projects() -> list[dict[str, Any]]:
    """
    List all projects that have valid, accessible paths.

    Returns:
        List of project info dicts with additional 'name' field.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        projects = session.query(Project).all()
        valid = []
        for p in projects:
            path = Path(p.path)
            is_valid, _ = validate_project_path(path)
            if is_valid:
                valid.append({
                    "name": p.name,
                    "path": p.path,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                })
        return valid
    finally:
        session.close()


# =============================================================================
# Settings CRUD Functions
# =============================================================================

def get_setting(key: str, default: str | None = None) -> str | None:
    """
    Get a setting value by key.

    Args:
        key: The setting key.
        default: Default value if setting doesn't exist or on DB error.

    Returns:
        The setting value, or default if not found or on error.
    """
    try:
        _, SessionLocal = _get_engine()
        session = SessionLocal()
        try:
            setting = session.query(Settings).filter(Settings.key == key).first()
            return setting.value if setting else default
        finally:
            session.close()
    except Exception as e:
        logger.warning("Failed to read setting '%s': %s", key, e)
        return default


def set_setting(key: str, value: str) -> None:
    """
    Set a setting value (creates or updates).

    Args:
        key: The setting key.
        value: The setting value.
    """
    with _get_session() as session:
        setting = session.query(Settings).filter(Settings.key == key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.now()
        else:
            setting = Settings(
                key=key,
                value=value,
                updated_at=datetime.now()
            )
            session.add(setting)

    logger.debug("Set setting '%s' = '%s'", key, value)


def get_all_settings() -> dict[str, str]:
    """
    Get all settings as a dictionary.

    Returns:
        Dictionary mapping setting keys to values.
    """
    try:
        _, SessionLocal = _get_engine()
        session = SessionLocal()
        try:
            settings = session.query(Settings).all()
            return {s.key: s.value for s in settings}
        finally:
            session.close()
    except Exception as e:
        logger.warning("Failed to read settings: %s", e)
        return {}


# =============================================================================
# Database Migration Functions
# =============================================================================

def _migrate_registry_db() -> None:
    """
    Migrate existing registry database to add new columns and tables.
    Called automatically when database is initialized.
    """
    from sqlalchemy import text

    engine, _ = _get_engine()

    with engine.connect() as conn:
        # Check and add new columns to projects table
        result = conn.execute(text("PRAGMA table_info(projects)"))
        columns = [row[1] for row in result.fetchall()]

        if "status" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
            logger.info("Added 'status' column to projects table")

        if "last_agent_run" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN last_agent_run DATETIME"))
            logger.info("Added 'last_agent_run' column to projects table")

        if "completion_percentage" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN completion_percentage FLOAT DEFAULT 0.0"))
            logger.info("Added 'completion_percentage' column to projects table")

        conn.commit()


# =============================================================================
# Project Status Functions
# =============================================================================

def update_project_status(name: str, status: str) -> bool:
    """
    Update a project's status.

    Args:
        name: The project name.
        status: New status (active/paused/finished/archived).

    Returns:
        True if updated, False if project wasn't found.
    """
    valid_statuses = {"active", "paused", "finished", "archived"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

    with _get_session() as session:
        project = session.query(Project).filter(Project.name == name).first()
        if not project:
            return False

        project.status = status
        logger.info("Updated project '%s' status to '%s'", name, status)

    return True


def update_project_completion(name: str, percentage: float) -> bool:
    """
    Update a project's completion percentage.

    Args:
        name: The project name.
        percentage: Completion percentage (0.0 to 100.0).

    Returns:
        True if updated, False if project wasn't found.
    """
    with _get_session() as session:
        project = session.query(Project).filter(Project.name == name).first()
        if not project:
            return False

        project.completion_percentage = min(max(percentage, 0.0), 100.0)

    return True


def update_project_last_run(name: str) -> bool:
    """
    Update a project's last agent run timestamp to now.

    Args:
        name: The project name.

    Returns:
        True if updated, False if project wasn't found.
    """
    with _get_session() as session:
        project = session.query(Project).filter(Project.name == name).first()
        if not project:
            return False

        project.last_agent_run = datetime.now()

    return True


def list_projects_by_status(status: str) -> list[dict[str, Any]]:
    """
    Get all projects with a specific status.

    Args:
        status: The status to filter by.

    Returns:
        List of project info dictionaries.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        projects = session.query(Project).filter(Project.status == status).all()
        return [
            {
                "name": p.name,
                "path": p.path,
                "status": p.status,
                "completion_percentage": p.completion_percentage or 0.0,
                "last_agent_run": p.last_agent_run.isoformat() if p.last_agent_run else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ]
    finally:
        session.close()


def get_project_by_status(status: str) -> dict[str, dict[str, Any]]:
    """
    Get projects filtered by status as a dictionary.

    Args:
        status: The status to filter by (active/paused/finished/archived).

    Returns:
        Dictionary mapping project names to their info dictionaries.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        # Handle None status as "active"
        if status == "active":
            projects = session.query(Project).filter(
                (Project.status == status) | (Project.status == None)
            ).all()
        else:
            projects = session.query(Project).filter(Project.status == status).all()

        return {
            p.name: {
                "path": p.path,
                "status": p.status or "active",
                "completion_percentage": p.completion_percentage or 0.0,
                "last_agent_run": p.last_agent_run.isoformat() if p.last_agent_run else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        }
    finally:
        session.close()


def get_all_projects_stats() -> dict[str, Any]:
    """
    Get aggregate statistics for all projects.

    Returns:
        Dictionary with counts by status.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        projects = session.query(Project).all()

        stats = {
            "total": len(projects),
            "active": 0,
            "paused": 0,
            "finished": 0,
            "archived": 0,
        }

        for p in projects:
            status = p.status or "active"
            if status in stats:
                stats[status] += 1

        return stats
    finally:
        session.close()


# =============================================================================
# Project Agent CRUD Functions
# =============================================================================

def create_project_agent(
    project_name: str,
    agent_id: str,
    mode: str = "separate",
    worktree_path: str | None = None
) -> dict[str, Any]:
    """
    Create a new agent entry for a project.

    Args:
        project_name: The project name.
        agent_id: Unique agent identifier (e.g., "agent-1").
        mode: Agent mode (separate/collaborative/worktree).
        worktree_path: Optional path to git worktree.

    Returns:
        The created agent info dictionary.
    """
    with _get_session() as session:
        agent = ProjectAgent(
            project_name=project_name,
            agent_id=agent_id,
            mode=mode,
            worktree_path=worktree_path,
            status="stopped",
            created_at=datetime.now()
        )
        session.add(agent)
        session.flush()

        return {
            "id": agent.id,
            "project_name": agent.project_name,
            "agent_id": agent.agent_id,
            "mode": agent.mode,
            "status": agent.status,
            "worktree_path": agent.worktree_path,
            "created_at": agent.created_at.isoformat(),
        }


def get_project_agents(project_name: str) -> list[dict[str, Any]]:
    """
    Get all agents for a project.

    Args:
        project_name: The project name.

    Returns:
        List of agent info dictionaries.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        agents = session.query(ProjectAgent).filter(
            ProjectAgent.project_name == project_name
        ).all()
        return [
            {
                "id": a.id,
                "project_name": a.project_name,
                "agent_id": a.agent_id,
                "mode": a.mode,
                "status": a.status,
                "current_feature_id": a.current_feature_id,
                "pid": a.pid,
                "started_at": a.started_at.isoformat() if a.started_at else None,
                "worktree_path": a.worktree_path,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in agents
        ]
    finally:
        session.close()


def get_project_agent(project_name: str, agent_id: str) -> dict[str, Any] | None:
    """
    Get a specific agent for a project.

    Args:
        project_name: The project name.
        agent_id: The agent identifier.

    Returns:
        Agent info dictionary, or None if not found.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        agent = session.query(ProjectAgent).filter(
            ProjectAgent.project_name == project_name,
            ProjectAgent.agent_id == agent_id
        ).first()
        if not agent:
            return None
        return {
            "id": agent.id,
            "project_name": agent.project_name,
            "agent_id": agent.agent_id,
            "mode": agent.mode,
            "status": agent.status,
            "current_feature_id": agent.current_feature_id,
            "pid": agent.pid,
            "started_at": agent.started_at.isoformat() if agent.started_at else None,
            "worktree_path": agent.worktree_path,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
        }
    finally:
        session.close()


def update_project_agent(
    project_name: str,
    agent_id: str,
    status: str | None = None,
    pid: int | None = None,
    current_feature_id: int | None = None,
    started_at: datetime | None = None
) -> bool:
    """
    Update an agent's status and metadata.

    Args:
        project_name: The project name.
        agent_id: The agent identifier.
        status: New status (optional).
        pid: Process ID (optional).
        current_feature_id: Feature being worked on (optional).
        started_at: Start timestamp (optional).

    Returns:
        True if updated, False if agent wasn't found.
    """
    with _get_session() as session:
        agent = session.query(ProjectAgent).filter(
            ProjectAgent.project_name == project_name,
            ProjectAgent.agent_id == agent_id
        ).first()
        if not agent:
            return False

        if status is not None:
            agent.status = status
        if pid is not None:
            agent.pid = pid
        if current_feature_id is not None:
            agent.current_feature_id = current_feature_id
        if started_at is not None:
            agent.started_at = started_at

    return True


def delete_project_agent(project_name: str, agent_id: str) -> bool:
    """
    Delete an agent from a project.

    Args:
        project_name: The project name.
        agent_id: The agent identifier.

    Returns:
        True if deleted, False if agent wasn't found.
    """
    with _get_session() as session:
        agent = session.query(ProjectAgent).filter(
            ProjectAgent.project_name == project_name,
            ProjectAgent.agent_id == agent_id
        ).first()
        if not agent:
            return False

        session.delete(agent)
        logger.info("Deleted agent '%s' from project '%s'", agent_id, project_name)

    return True


def get_next_agent_id(project_name: str) -> str:
    """
    Get the next available agent ID for a project.

    Args:
        project_name: The project name.

    Returns:
        Next agent ID (e.g., "agent-1", "agent-2").
    """
    agents = get_project_agents(project_name)
    if not agents:
        return "agent-1"

    # Find the highest number and increment
    max_num = 0
    for agent in agents:
        aid = agent["agent_id"]
        if aid.startswith("agent-"):
            try:
                num = int(aid.split("-")[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass

    return f"agent-{max_num + 1}"


# =============================================================================
# Project Config CRUD Functions
# =============================================================================

def get_project_config(project_name: str) -> dict[str, Any] | None:
    """
    Get configuration for a project.

    Args:
        project_name: The project name.

    Returns:
        Config dictionary, or None if not found.
    """
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        config = session.query(ProjectConfig).filter(
            ProjectConfig.project_name == project_name
        ).first()
        if not config:
            return None
        return {
            "project_name": config.project_name,
            "max_parallel_agents": config.max_parallel_agents,
            "default_mode": config.default_mode,
            "use_worktrees": config.use_worktrees,
            "auto_stop_on_completion": config.auto_stop_on_completion,
            "subagent_config": config.subagent_config,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None,
        }
    finally:
        session.close()


def create_or_update_project_config(
    project_name: str,
    max_parallel_agents: int | None = None,
    default_mode: str | None = None,
    use_worktrees: bool | None = None,
    auto_stop_on_completion: bool | None = None,
    subagent_config: dict | None = None
) -> dict[str, Any]:
    """
    Create or update configuration for a project.

    Args:
        project_name: The project name.
        max_parallel_agents: Maximum number of parallel agents.
        default_mode: Default agent mode.
        use_worktrees: Whether to use git worktrees.
        auto_stop_on_completion: Whether to auto-stop on completion.
        subagent_config: Custom subagent configuration.

    Returns:
        The updated config dictionary.
    """
    with _get_session() as session:
        config = session.query(ProjectConfig).filter(
            ProjectConfig.project_name == project_name
        ).first()

        if not config:
            config = ProjectConfig(
                project_name=project_name,
                max_parallel_agents=max_parallel_agents or 1,
                default_mode=default_mode or "separate",
                use_worktrees=use_worktrees if use_worktrees is not None else False,
                auto_stop_on_completion=auto_stop_on_completion if auto_stop_on_completion is not None else True,
                subagent_config=subagent_config,
                updated_at=datetime.now()
            )
            session.add(config)
        else:
            if max_parallel_agents is not None:
                config.max_parallel_agents = max_parallel_agents
            if default_mode is not None:
                config.default_mode = default_mode
            if use_worktrees is not None:
                config.use_worktrees = use_worktrees
            if auto_stop_on_completion is not None:
                config.auto_stop_on_completion = auto_stop_on_completion
            if subagent_config is not None:
                config.subagent_config = subagent_config
            config.updated_at = datetime.now()

        session.flush()

        return {
            "project_name": config.project_name,
            "max_parallel_agents": config.max_parallel_agents,
            "default_mode": config.default_mode,
            "use_worktrees": config.use_worktrees,
            "auto_stop_on_completion": config.auto_stop_on_completion,
            "subagent_config": config.subagent_config,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None,
        }


def get_or_create_default_config(project_name: str) -> dict[str, Any]:
    """
    Get config for a project, creating default if it doesn't exist.

    Args:
        project_name: The project name.

    Returns:
        Config dictionary.
    """
    config = get_project_config(project_name)
    if config:
        return config
    return create_or_update_project_config(project_name)
