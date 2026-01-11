"""
Database Models and Connection
==============================

SQLite database schema for feature storage using SQLAlchemy.
"""

from pathlib import Path
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.types import JSON

Base = declarative_base()


class Feature(Base):
    """Feature model representing a test case/feature to implement."""

    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    priority = Column(Integer, nullable=False, default=999, index=True)
    category = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    steps = Column(JSON, nullable=False)  # Stored as JSON array
    passes = Column(Boolean, default=False, index=True)
    in_progress = Column(Boolean, default=False, index=True)
    # New columns for multi-agent support
    assigned_agent_id = Column(String(50), nullable=True, index=True)  # Which agent is working on this
    attempt_count = Column(Integer, default=0)  # Number of attempts to complete
    last_attempt_at = Column(DateTime, nullable=True)  # Last attempt timestamp
    added_at = Column(DateTime, nullable=True)  # When feature was added (for tracking new features)
    source = Column(String(20), default="initializer")  # initializer/manual/user_added

    def to_dict(self) -> dict:
        """Convert feature to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "priority": self.priority,
            "category": self.category,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "passes": self.passes,
            "in_progress": self.in_progress,
            "assigned_agent_id": self.assigned_agent_id,
            "attempt_count": self.attempt_count,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "source": self.source,
        }


def get_database_path(project_dir: Path) -> Path:
    """Return the path to the SQLite database for a project."""
    return project_dir / "features.db"


def get_database_url(project_dir: Path) -> str:
    """Return the SQLAlchemy database URL for a project.

    Uses POSIX-style paths (forward slashes) for cross-platform compatibility.
    """
    db_path = get_database_path(project_dir)
    return f"sqlite:///{db_path.as_posix()}"


def _migrate_features_db(engine) -> None:
    """Add missing columns to existing databases."""
    from sqlalchemy import text

    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("PRAGMA table_info(features)"))
        columns = [row[1] for row in result.fetchall()]

        # Add in_progress column (legacy migration)
        if "in_progress" not in columns:
            conn.execute(text("ALTER TABLE features ADD COLUMN in_progress BOOLEAN DEFAULT 0"))

        # Add new multi-agent columns
        if "assigned_agent_id" not in columns:
            conn.execute(text("ALTER TABLE features ADD COLUMN assigned_agent_id VARCHAR(50)"))

        if "attempt_count" not in columns:
            conn.execute(text("ALTER TABLE features ADD COLUMN attempt_count INTEGER DEFAULT 0"))

        if "last_attempt_at" not in columns:
            conn.execute(text("ALTER TABLE features ADD COLUMN last_attempt_at DATETIME"))

        if "added_at" not in columns:
            conn.execute(text("ALTER TABLE features ADD COLUMN added_at DATETIME"))

        if "source" not in columns:
            conn.execute(text("ALTER TABLE features ADD COLUMN source VARCHAR(20) DEFAULT 'initializer'"))

        conn.commit()


def create_database(project_dir: Path) -> tuple:
    """
    Create database and return engine + session maker.

    Args:
        project_dir: Directory containing the project

    Returns:
        Tuple of (engine, SessionLocal)
    """
    db_url = get_database_url(project_dir)
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    # Migrate existing databases to add new columns
    _migrate_features_db(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


# Global session maker - will be set when server starts
_session_maker: Optional[sessionmaker] = None


def set_session_maker(session_maker: sessionmaker) -> None:
    """Set the global session maker."""
    global _session_maker
    _session_maker = session_maker


def get_db() -> Session:
    """
    Dependency for FastAPI to get database session.

    Yields a database session and ensures it's closed after use.
    """
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call set_session_maker first.")

    db = _session_maker()
    try:
        yield db
    finally:
        db.close()
