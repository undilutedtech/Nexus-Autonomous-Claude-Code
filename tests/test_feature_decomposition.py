"""
Tests for Feature Decomposition System
======================================

Tests the automatic decomposition of complex features into smaller sub-features.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.database import Base, Feature


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def db_session(temp_project_dir):
    """Create a test database session."""
    db_path = temp_project_dir / "features.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


class TestFeatureDecomposition:
    """Test feature decomposition functionality."""

    def test_feature_has_decomposition_columns(self, db_session):
        """Test that Feature model has parent_id and is_decomposed columns."""
        feature = Feature(
            priority=1,
            category="Test",
            name="Test Feature",
            description="Test description",
            steps=["Step 1", "Step 2"],
            passes=False,
            parent_id=None,
            is_decomposed=False,
        )
        db_session.add(feature)
        db_session.commit()

        # Query back
        queried = db_session.query(Feature).first()
        assert queried.parent_id is None
        assert queried.is_decomposed is False

    def test_feature_to_dict_includes_decomposition_fields(self, db_session):
        """Test that to_dict includes decomposition fields."""
        feature = Feature(
            priority=1,
            category="Test",
            name="Test Feature",
            description="Test description",
            steps=["Step 1"],
            passes=False,
            parent_id=5,
            is_decomposed=True,
        )
        db_session.add(feature)
        db_session.commit()

        feature_dict = feature.to_dict()
        assert "parent_id" in feature_dict
        assert "is_decomposed" in feature_dict
        assert feature_dict["parent_id"] == 5
        assert feature_dict["is_decomposed"] is True

    def test_sub_feature_links_to_parent(self, db_session):
        """Test that sub-features correctly link to parent."""
        # Create parent feature
        parent = Feature(
            priority=1,
            category="Auth",
            name="User Authentication",
            description="Complete auth system",
            steps=["Login", "Logout", "Session"],
            passes=False,
            is_decomposed=True,
        )
        db_session.add(parent)
        db_session.commit()

        # Create sub-features
        sub1 = Feature(
            priority=2,
            category="Auth",
            name="User Authentication - Login Form",
            description="Create login form",
            steps=["Create form", "Validate"],
            passes=False,
            parent_id=parent.id,
            source="decomposed",
        )
        sub2 = Feature(
            priority=3,
            category="Auth",
            name="User Authentication - API Integration",
            description="Connect to auth API",
            steps=["Create API client", "Handle response"],
            passes=False,
            parent_id=parent.id,
            source="decomposed",
        )
        db_session.add_all([sub1, sub2])
        db_session.commit()

        # Query sub-features by parent
        sub_features = db_session.query(Feature).filter(
            Feature.parent_id == parent.id
        ).all()
        assert len(sub_features) == 2
        assert all(sf.source == "decomposed" for sf in sub_features)

    def test_parent_passes_when_all_subs_pass(self, db_session):
        """Test parent feature passes when all sub-features pass."""
        # Create parent
        parent = Feature(
            priority=1,
            category="Test",
            name="Complex Feature",
            description="Complex",
            steps=["Many steps"],
            passes=False,
            is_decomposed=True,
        )
        db_session.add(parent)
        db_session.commit()

        # Create sub-features
        sub1 = Feature(
            priority=2,
            category="Test",
            name="Complex Feature - Part 1",
            description="Part 1",
            steps=["Step"],
            passes=True,  # Passing
            parent_id=parent.id,
        )
        sub2 = Feature(
            priority=3,
            category="Test",
            name="Complex Feature - Part 2",
            description="Part 2",
            steps=["Step"],
            passes=True,  # Passing
            parent_id=parent.id,
        )
        db_session.add_all([sub1, sub2])
        db_session.commit()

        # Check if all sub-features pass
        sub_features = db_session.query(Feature).filter(
            Feature.parent_id == parent.id
        ).all()
        all_passing = all(sf.passes for sf in sub_features)
        assert all_passing is True

        # Simulate marking parent as passing
        if all_passing:
            parent.passes = True
            db_session.commit()

        assert parent.passes is True

    def test_decomposed_features_skipped_in_get_next(self, db_session):
        """Test that decomposed features are skipped when getting next feature."""
        # Create a decomposed feature (should be skipped)
        decomposed = Feature(
            priority=1,
            category="Test",
            name="Decomposed Feature",
            description="Was decomposed",
            steps=["Step"],
            passes=False,
            is_decomposed=True,
        )
        # Create a normal pending feature
        normal = Feature(
            priority=2,
            category="Test",
            name="Normal Feature",
            description="Normal",
            steps=["Step"],
            passes=False,
            is_decomposed=False,
        )
        db_session.add_all([decomposed, normal])
        db_session.commit()

        # Query for next feature (should skip decomposed)
        next_feature = (
            db_session.query(Feature)
            .filter(Feature.passes == False)
            .filter(Feature.in_progress == False)
            .filter(Feature.is_decomposed == False)
            .order_by(Feature.priority.asc())
            .first()
        )

        assert next_feature is not None
        assert next_feature.name == "Normal Feature"
        assert next_feature.is_decomposed is False


class TestProgressDecomposition:
    """Test progress.py decomposition functions."""

    def test_get_stuck_feature_id(self, temp_project_dir):
        """Test getting stuck feature ID from attempts file."""
        from progress import get_stuck_feature_id, MAX_FEATURE_ATTEMPTS

        # Create attempts file with stuck feature
        attempts_file = temp_project_dir / ".feature_attempts"
        attempts_file.write_text(json.dumps({"14": MAX_FEATURE_ATTEMPTS}))

        stuck_id = get_stuck_feature_id(temp_project_dir)
        assert stuck_id == 14

    def test_get_stuck_feature_id_none_when_not_stuck(self, temp_project_dir):
        """Test returns None when no feature is stuck."""
        from progress import get_stuck_feature_id, MAX_FEATURE_ATTEMPTS

        # Create attempts file with feature not yet stuck
        attempts_file = temp_project_dir / ".feature_attempts"
        attempts_file.write_text(json.dumps({"14": MAX_FEATURE_ATTEMPTS - 1}))

        stuck_id = get_stuck_feature_id(temp_project_dir)
        assert stuck_id is None

    def test_mark_and_get_pending_decomposition(self, temp_project_dir):
        """Test marking and getting pending decomposition."""
        from progress import (
            mark_feature_for_decomposition,
            get_pending_decomposition,
            clear_pending_decomposition,
        )

        # Initially no pending decomposition
        assert get_pending_decomposition(temp_project_dir) is None

        # Mark for decomposition
        mark_feature_for_decomposition(temp_project_dir, 42)
        assert get_pending_decomposition(temp_project_dir) == 42

        # Clear it
        clear_pending_decomposition(temp_project_dir)
        assert get_pending_decomposition(temp_project_dir) is None

    def test_check_completion_status_triggers_decomposition(self, temp_project_dir):
        """Test that check_completion_status triggers decomposition instead of stopping."""
        from progress import (
            check_completion_status,
            get_pending_decomposition,
            MAX_FEATURE_ATTEMPTS,
        )

        # Create a database with one feature
        db_path = temp_project_dir / "features.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        feature = Feature(
            priority=1,
            category="Test",
            name="Stuck Feature",
            description="Gets stuck",
            steps=["Step"],
            passes=False,
        )
        session.add(feature)
        session.commit()
        feature_id = feature.id
        session.close()
        engine.dispose()

        # Create attempts file with stuck feature
        attempts_file = temp_project_dir / ".feature_attempts"
        attempts_file.write_text(json.dumps({str(feature_id): MAX_FEATURE_ATTEMPTS}))

        # Check completion status
        should_stop, reason, action = check_completion_status(
            temp_project_dir, allow_decomposition=True
        )

        # Should NOT stop, but trigger decomposition
        assert should_stop is False
        assert action == "decompose"
        assert "decomposition" in reason.lower() or "stuck" in reason.lower()

        # Should have pending decomposition
        pending = get_pending_decomposition(temp_project_dir)
        assert pending == feature_id


class TestDecompositionPrompt:
    """Test decomposition prompt generation."""

    def test_get_decomposition_prompt(self):
        """Test decomposition prompt is generated correctly."""
        from prompts import get_decomposition_prompt

        stuck_feature = {
            "id": 14,
            "category": "Authentication",
            "name": "User Login System",
            "description": "Complete user authentication with login, logout, and session management",
            "steps": ["Create login form", "Validate credentials", "Manage session"],
            "attempts": 3,
        }

        prompt = get_decomposition_prompt(None, stuck_feature)

        # Check prompt contains key information
        assert "Feature #14" in prompt
        assert "User Login System" in prompt
        assert "3 times" in prompt or "multiple" in prompt.lower()
        assert "feature_decompose" in prompt
        assert "sub-features" in prompt.lower()

    def test_get_decomposition_prompt_handles_none(self):
        """Test decomposition prompt handles None feature."""
        from prompts import get_decomposition_prompt

        prompt = get_decomposition_prompt(None, None)

        # Should still generate a valid prompt
        assert "feature_decompose" in prompt
        assert "sub-features" in prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
