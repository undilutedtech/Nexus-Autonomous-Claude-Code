#!/usr/bin/env python3
"""
MCP Server for Feature Management
==================================

Provides tools to manage features in the autonomous coding system,
replacing the previous FastAPI-based REST API.

Tools:
- feature_get_stats: Get progress statistics
- feature_get_next: Get next feature to implement
- feature_get_for_regression: Get random passing features for testing
- feature_mark_passing: Mark a feature as passing
- feature_skip: Skip a feature (move to end of queue)
- feature_mark_in_progress: Mark a feature as in-progress
- feature_clear_in_progress: Clear in-progress status
- feature_create_bulk: Create multiple features at once
- ask_user_question: Ask the user a clarifying question and wait for response
"""

import json
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from sqlalchemy.sql.expression import func

# Add parent directory to path so we can import from api module
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import Feature, create_database
from api.migration import migrate_json_to_sqlite
from server.services.agent_questions import (
    add_question,
    get_answer,
    get_pending_question,
)
from server.services.code_validator import (
    validate_project,
    scan_file,
    CODE_EXTENSIONS,
)
from server.services.doc_generator import (
    generate_technical_documentation,
    analyze_project_structure,
)

# Configuration from environment
PROJECT_DIR = Path(os.environ.get("PROJECT_DIR", ".")).resolve()


# Pydantic models for input validation
class MarkPassingInput(BaseModel):
    """Input for marking a feature as passing."""
    feature_id: int = Field(..., description="The ID of the feature to mark as passing", ge=1)


class SkipFeatureInput(BaseModel):
    """Input for skipping a feature."""
    feature_id: int = Field(..., description="The ID of the feature to skip", ge=1)


class MarkInProgressInput(BaseModel):
    """Input for marking a feature as in-progress."""
    feature_id: int = Field(..., description="The ID of the feature to mark as in-progress", ge=1)


class ClearInProgressInput(BaseModel):
    """Input for clearing in-progress status."""
    feature_id: int = Field(..., description="The ID of the feature to clear in-progress status", ge=1)


class RegressionInput(BaseModel):
    """Input for getting regression features."""
    limit: int = Field(default=3, ge=1, le=10, description="Maximum number of passing features to return")


class FeatureCreateItem(BaseModel):
    """Schema for creating a single feature."""
    category: str = Field(..., min_length=1, max_length=100, description="Feature category")
    name: str = Field(..., min_length=1, max_length=255, description="Feature name")
    description: str = Field(..., min_length=1, description="Detailed description")
    steps: list[str] = Field(..., min_length=1, description="Implementation/test steps")


class BulkCreateInput(BaseModel):
    """Input for bulk creating features."""
    features: list[FeatureCreateItem] = Field(..., min_length=1, description="List of features to create")


class SubFeatureItem(BaseModel):
    """Schema for a sub-feature when decomposing."""
    name: str = Field(..., min_length=1, max_length=255, description="Sub-feature name")
    description: str = Field(..., min_length=1, description="What this sub-feature accomplishes")
    steps: list[str] = Field(..., min_length=1, description="Implementation steps for this sub-feature")


# Global database session maker (initialized on startup)
_session_maker = None
_engine = None


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Initialize database on startup, cleanup on shutdown."""
    global _session_maker, _engine

    # Create project directory if it doesn't exist
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize database
    _engine, _session_maker = create_database(PROJECT_DIR)

    # Run migration if needed (converts legacy JSON to SQLite)
    migrate_json_to_sqlite(PROJECT_DIR, _session_maker)

    yield

    # Cleanup
    if _engine:
        _engine.dispose()


# Initialize the MCP server
mcp = FastMCP("features", lifespan=server_lifespan)


def get_session():
    """Get a new database session."""
    if _session_maker is None:
        raise RuntimeError("Database not initialized")
    return _session_maker()


@mcp.tool()
def feature_get_stats() -> str:
    """Get statistics about feature completion progress.

    Returns the number of passing features, in-progress features, total features,
    and completion percentage. Use this to track overall progress of the implementation.

    Returns:
        JSON with: passing (int), in_progress (int), total (int), percentage (float)
    """
    session = get_session()
    try:
        total = session.query(Feature).count()
        passing = session.query(Feature).filter(Feature.passes == True).count()
        in_progress = session.query(Feature).filter(Feature.in_progress == True).count()
        percentage = round((passing / total) * 100, 1) if total > 0 else 0.0

        return json.dumps({
            "passing": passing,
            "in_progress": in_progress,
            "total": total,
            "percentage": percentage
        }, indent=2)
    finally:
        session.close()


@mcp.tool()
def feature_get_next() -> str:
    """Get the highest-priority pending feature to work on.

    Returns the feature with the lowest priority number that has passes=false
    AND is not currently in-progress by another agent.
    Use this at the start of each coding session to determine what to implement next.

    Decomposed features are skipped (their sub-features should be worked on instead).

    Returns:
        JSON with feature details (id, priority, category, name, description, steps, passes, in_progress)
        or error message if all features are passing or being worked on.
    """
    session = get_session()
    try:
        # Filter out passing, in-progress, AND decomposed features
        # Decomposed features will auto-pass when their sub-features pass
        feature = (
            session.query(Feature)
            .filter(Feature.passes == False)
            .filter(Feature.in_progress == False)
            .filter(Feature.is_decomposed == False)
            .order_by(Feature.priority.asc(), Feature.id.asc())
            .first()
        )

        if feature is None:
            # Check if there are any non-passing features at all
            any_pending = (
                session.query(Feature)
                .filter(Feature.passes == False)
                .filter(Feature.is_decomposed == False)
                .first()
            )
            if any_pending:
                return json.dumps({"error": "All pending features are currently being worked on by other agents. Wait for them to complete."})
            return json.dumps({"error": "All features are passing! No more work to do."})

        return json.dumps(feature.to_dict(), indent=2)
    finally:
        session.close()


@mcp.tool()
def feature_get_for_regression(
    limit: Annotated[int, Field(default=3, ge=1, le=10, description="Maximum number of passing features to return")] = 3
) -> str:
    """Get random passing features for regression testing.

    Returns a random selection of features that are currently passing.
    Use this to verify that previously implemented features still work
    after making changes.

    Args:
        limit: Maximum number of features to return (1-10, default 3)

    Returns:
        JSON with: features (list of feature objects), count (int)
    """
    session = get_session()
    try:
        features = (
            session.query(Feature)
            .filter(Feature.passes == True)
            .order_by(func.random())
            .limit(limit)
            .all()
        )

        return json.dumps({
            "features": [f.to_dict() for f in features],
            "count": len(features)
        }, indent=2)
    finally:
        session.close()


@mcp.tool()
def feature_mark_passing(
    feature_id: Annotated[int, Field(description="The ID of the feature to mark as passing", ge=1)]
) -> str:
    """Mark a feature as passing after successful implementation.

    Updates the feature's passes field to true and clears the in_progress flag.
    Use this after you have implemented the feature and verified it works correctly.

    If this feature is a sub-feature (has a parent_id), this will also check if
    all sibling sub-features are passing and automatically mark the parent as
    passing if so.

    Args:
        feature_id: The ID of the feature to mark as passing

    Returns:
        JSON with the updated feature details, or error if not found.
    """
    session = get_session()
    try:
        feature = session.query(Feature).filter(Feature.id == feature_id).first()

        if feature is None:
            return json.dumps({"error": f"Feature with ID {feature_id} not found"})

        feature.passes = True
        feature.in_progress = False
        session.commit()
        session.refresh(feature)

        result = feature.to_dict()

        # If this is a sub-feature, check if parent should be marked complete
        if feature.parent_id:
            parent = session.query(Feature).filter(Feature.id == feature.parent_id).first()
            if parent and parent.is_decomposed:
                # Check all sub-features
                sub_features = (
                    session.query(Feature)
                    .filter(Feature.parent_id == parent.id)
                    .all()
                )
                all_passing = all(sf.passes for sf in sub_features)

                if all_passing and not parent.passes:
                    parent.passes = True
                    parent.in_progress = False
                    session.commit()
                    result["parent_completed"] = {
                        "id": parent.id,
                        "name": parent.name,
                        "message": "All sub-features complete! Parent feature marked as passing."
                    }

        return json.dumps(result, indent=2)
    finally:
        session.close()


@mcp.tool()
def feature_skip(
    feature_id: Annotated[int, Field(description="The ID of the feature to skip", ge=1)]
) -> str:
    """Skip a feature by moving it to the end of the priority queue.

    Use this when a feature cannot be implemented yet due to:
    - Dependencies on other features that aren't implemented yet
    - External blockers (missing assets, unclear requirements)
    - Technical prerequisites that need to be addressed first

    The feature's priority is set to max_priority + 1, so it will be
    worked on after all other pending features. Also clears the in_progress
    flag so the feature returns to "pending" status.

    Args:
        feature_id: The ID of the feature to skip

    Returns:
        JSON with skip details: id, name, old_priority, new_priority, message
    """
    session = get_session()
    try:
        feature = session.query(Feature).filter(Feature.id == feature_id).first()

        if feature is None:
            return json.dumps({"error": f"Feature with ID {feature_id} not found"})

        if feature.passes:
            return json.dumps({"error": "Cannot skip a feature that is already passing"})

        old_priority = feature.priority

        # Get max priority and set this feature to max + 1
        max_priority_result = session.query(Feature.priority).order_by(Feature.priority.desc()).first()
        new_priority = (max_priority_result[0] + 1) if max_priority_result else 1

        feature.priority = new_priority
        feature.in_progress = False
        session.commit()
        session.refresh(feature)

        return json.dumps({
            "id": feature.id,
            "name": feature.name,
            "old_priority": old_priority,
            "new_priority": new_priority,
            "message": f"Feature '{feature.name}' moved to end of queue"
        }, indent=2)
    finally:
        session.close()


@mcp.tool()
def feature_mark_in_progress(
    feature_id: Annotated[int, Field(description="The ID of the feature to mark as in-progress", ge=1)]
) -> str:
    """Mark a feature as in-progress. Call immediately after feature_get_next().

    This prevents other agent sessions from working on the same feature.
    Use this as soon as you retrieve a feature to work on.

    Args:
        feature_id: The ID of the feature to mark as in-progress

    Returns:
        JSON with the updated feature details, or error if not found or already in-progress.
    """
    session = get_session()
    try:
        feature = session.query(Feature).filter(Feature.id == feature_id).first()

        if feature is None:
            return json.dumps({"error": f"Feature with ID {feature_id} not found"})

        if feature.passes:
            return json.dumps({"error": f"Feature with ID {feature_id} is already passing"})

        if feature.in_progress:
            return json.dumps({"error": f"Feature with ID {feature_id} is already in-progress"})

        feature.in_progress = True
        session.commit()
        session.refresh(feature)

        return json.dumps(feature.to_dict(), indent=2)
    finally:
        session.close()


@mcp.tool()
def feature_clear_in_progress(
    feature_id: Annotated[int, Field(description="The ID of the feature to clear in-progress status", ge=1)]
) -> str:
    """Clear in-progress status from a feature.

    Use this when abandoning a feature or manually unsticking a stuck feature.
    The feature will return to the pending queue.

    Args:
        feature_id: The ID of the feature to clear in-progress status

    Returns:
        JSON with the updated feature details, or error if not found.
    """
    session = get_session()
    try:
        feature = session.query(Feature).filter(Feature.id == feature_id).first()

        if feature is None:
            return json.dumps({"error": f"Feature with ID {feature_id} not found"})

        feature.in_progress = False
        session.commit()
        session.refresh(feature)

        return json.dumps(feature.to_dict(), indent=2)
    finally:
        session.close()


@mcp.tool()
def feature_create_bulk(
    features: Annotated[list[dict], Field(description="List of features to create, each with category, name, description, and steps")]
) -> str:
    """Create multiple features in a single operation.

    Features are assigned sequential priorities based on their order.
    All features start with passes=false.

    This is typically used by the initializer agent to set up the initial
    feature list from the app specification.

    Args:
        features: List of features to create, each with:
            - category (str): Feature category
            - name (str): Feature name
            - description (str): Detailed description
            - steps (list[str]): Implementation/test steps

    Returns:
        JSON with: created (int) - number of features created
    """
    session = get_session()
    try:
        # Get the starting priority
        max_priority_result = session.query(Feature.priority).order_by(Feature.priority.desc()).first()
        start_priority = (max_priority_result[0] + 1) if max_priority_result else 1

        created_count = 0
        for i, feature_data in enumerate(features):
            # Validate required fields
            if not all(key in feature_data for key in ["category", "name", "description", "steps"]):
                return json.dumps({
                    "error": f"Feature at index {i} missing required fields (category, name, description, steps)"
                })

            db_feature = Feature(
                priority=start_priority + i,
                category=feature_data["category"],
                name=feature_data["name"],
                description=feature_data["description"],
                steps=feature_data["steps"],
                passes=False,
            )
            session.add(db_feature)
            created_count += 1

        session.commit()

        return json.dumps({"created": created_count}, indent=2)
    except Exception as e:
        session.rollback()
        return json.dumps({"error": str(e)})
    finally:
        session.close()


@mcp.tool()
def feature_decompose(
    feature_id: Annotated[int, Field(description="The ID of the complex feature to decompose", ge=1)],
    sub_features: Annotated[list[dict], Field(description="List of smaller sub-features to create, each with name, description, and steps")],
    reason: Annotated[Optional[str], Field(default=None, description="Why this feature needs to be decomposed")] = None,
) -> str:
    """Decompose a complex feature into smaller, more manageable sub-features.

    Use this tool when a feature is too complex to implement in one go, or when
    you've attempted a feature multiple times without success. Breaking it down
    into smaller pieces makes each piece easier to implement and test.

    The original feature will be marked as 'decomposed' and its sub-features
    will be added to the queue with sequential priorities right after the parent.

    The parent feature will automatically pass when ALL its sub-features pass.

    Args:
        feature_id: The ID of the feature to decompose
        sub_features: List of sub-features, each with:
            - name (str): Brief name for the sub-feature
            - description (str): What this sub-feature accomplishes
            - steps (list[str]): Implementation/verification steps
        reason: Optional explanation for why decomposition was needed

    Returns:
        JSON with decomposition results including created sub-feature IDs

    Example:
        feature_decompose(
            feature_id=14,
            sub_features=[
                {
                    "name": "User authentication - Login form UI",
                    "description": "Create the login form with email and password fields",
                    "steps": ["Create LoginForm component", "Add validation", "Style the form"]
                },
                {
                    "name": "User authentication - API integration",
                    "description": "Connect login form to authentication API",
                    "steps": ["Create auth API client", "Handle login request", "Store auth token"]
                },
                {
                    "name": "User authentication - Session management",
                    "description": "Manage user session state across the app",
                    "steps": ["Create auth context", "Implement logout", "Add protected routes"]
                }
            ],
            reason="Feature too complex - breaking into UI, API, and session management"
        )
    """
    session = get_session()
    try:
        # Get the parent feature
        parent = session.query(Feature).filter(Feature.id == feature_id).first()

        if parent is None:
            return json.dumps({"error": f"Feature with ID {feature_id} not found"})

        if parent.passes:
            return json.dumps({"error": "Cannot decompose a feature that is already passing"})

        if parent.is_decomposed:
            return json.dumps({"error": "Feature is already decomposed"})

        if len(sub_features) < 2:
            return json.dumps({"error": "Must provide at least 2 sub-features when decomposing"})

        # Validate sub-features
        for i, sf in enumerate(sub_features):
            if not all(key in sf for key in ["name", "description", "steps"]):
                return json.dumps({
                    "error": f"Sub-feature at index {i} missing required fields (name, description, steps)"
                })
            if not isinstance(sf["steps"], list) or len(sf["steps"]) == 0:
                return json.dumps({
                    "error": f"Sub-feature at index {i} must have at least one step"
                })

        # Calculate priorities: insert sub-features right after parent
        # Shift all features after parent's priority down
        parent_priority = parent.priority
        shift_amount = len(sub_features)

        # Shift priorities of features after the parent
        features_to_shift = (
            session.query(Feature)
            .filter(Feature.priority > parent_priority)
            .filter(Feature.id != feature_id)
            .all()
        )
        for f in features_to_shift:
            f.priority += shift_amount

        # Create sub-features
        created_ids = []
        for i, sf in enumerate(sub_features):
            sub_feature = Feature(
                priority=parent_priority + 1 + i,
                category=parent.category,
                name=sf["name"],
                description=sf["description"],
                steps=sf["steps"],
                passes=False,
                in_progress=False,
                parent_id=parent.id,
                source="decomposed",
            )
            session.add(sub_feature)
            session.flush()  # Get the ID
            created_ids.append(sub_feature.id)

        # Mark parent as decomposed (not passing yet - will pass when all children pass)
        parent.is_decomposed = True
        parent.in_progress = False
        parent.attempt_count = 0  # Reset attempts

        session.commit()

        # Clear stuck detection for this feature (file-based tracking)
        try:
            attempts_file = PROJECT_DIR / ".feature_attempts"
            if attempts_file.exists():
                import json as json_module
                attempts_data = json_module.loads(attempts_file.read_text())
                if str(feature_id) in attempts_data:
                    del attempts_data[str(feature_id)]
                    attempts_file.write_text(json_module.dumps(attempts_data))
        except Exception:
            pass  # Non-critical

        return json.dumps({
            "success": True,
            "parent_id": feature_id,
            "parent_name": parent.name,
            "sub_feature_ids": created_ids,
            "sub_feature_count": len(created_ids),
            "reason": reason,
            "message": f"Decomposed '{parent.name}' into {len(created_ids)} sub-features. "
                      f"Parent will auto-pass when all sub-features pass.",
        }, indent=2)

    except Exception as e:
        session.rollback()
        return json.dumps({"error": str(e)})
    finally:
        session.close()


@mcp.tool()
def feature_check_parent_completion(
    parent_id: Annotated[int, Field(description="The ID of the parent feature to check", ge=1)]
) -> str:
    """Check if all sub-features of a decomposed feature are passing.

    If all sub-features are passing, the parent feature will be automatically
    marked as passing.

    This is called automatically after marking sub-features as passing, but
    can also be called manually to verify completion status.

    Args:
        parent_id: The ID of the parent feature to check

    Returns:
        JSON with parent completion status and sub-feature details
    """
    session = get_session()
    try:
        parent = session.query(Feature).filter(Feature.id == parent_id).first()

        if parent is None:
            return json.dumps({"error": f"Feature with ID {parent_id} not found"})

        if not parent.is_decomposed:
            return json.dumps({"error": "Feature is not decomposed"})

        # Get all sub-features
        sub_features = (
            session.query(Feature)
            .filter(Feature.parent_id == parent_id)
            .all()
        )

        if not sub_features:
            return json.dumps({"error": "No sub-features found for this parent"})

        passing_count = sum(1 for sf in sub_features if sf.passes)
        total_count = len(sub_features)
        all_passing = passing_count == total_count

        # If all sub-features pass, mark parent as passing
        if all_passing and not parent.passes:
            parent.passes = True
            parent.in_progress = False
            session.commit()

        return json.dumps({
            "parent_id": parent_id,
            "parent_name": parent.name,
            "parent_passes": parent.passes,
            "sub_features": {
                "total": total_count,
                "passing": passing_count,
                "remaining": total_count - passing_count,
            },
            "all_complete": all_passing,
            "message": "All sub-features complete! Parent marked as passing." if all_passing
                      else f"{passing_count}/{total_count} sub-features passing",
        }, indent=2)

    finally:
        session.close()


@mcp.tool()
def ask_user_question(
    question: Annotated[str, Field(description="The question to ask the user")],
    context: Annotated[Optional[str], Field(default=None, description="Additional context to help the user understand the question")] = None,
    options: Annotated[Optional[list[str]], Field(default=None, description="Optional list of choices for the user to pick from")] = None,
    timeout_seconds: Annotated[int, Field(default=300, ge=30, le=3600, description="How long to wait for an answer (30-3600 seconds, default 300)")] = 300,
) -> str:
    """Ask the user a clarifying question and wait for their response.

    Use this tool when you need user input to proceed with a task. The question
    will be displayed in the UI, and the tool will wait until the user provides
    an answer or the timeout is reached.

    Common use cases:
    - Choosing between implementation approaches
    - Confirming design decisions
    - Getting preferences for styling, naming, etc.
    - Clarifying ambiguous requirements

    Args:
        question: The question to ask the user (be clear and specific)
        context: Optional background information to help the user understand
        options: Optional list of choices (user can also provide custom answer)
        timeout_seconds: How long to wait for answer (default 5 minutes)

    Returns:
        JSON with the user's answer, or error if timeout/skipped.

    Example:
        ask_user_question(
            question="Which CSS framework should I use for styling?",
            context="The app needs responsive design with a modern look.",
            options=["Tailwind CSS", "Bootstrap", "Plain CSS"]
        )
    """
    try:
        # Create the question
        agent_question = add_question(
            project_dir=PROJECT_DIR,
            question=question,
            context=context,
            options=options,
        )

        question_id = agent_question.id
        print(f"[ASK_USER] Question created: {question_id}", file=sys.stderr)
        print(f"[ASK_USER] Waiting for user response (timeout: {timeout_seconds}s)...", file=sys.stderr)

        # Poll for answer
        start_time = time.time()
        poll_interval = 1.0  # Check every second

        while True:
            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                return json.dumps({
                    "error": "timeout",
                    "message": f"No response received within {timeout_seconds} seconds",
                    "question_id": question_id,
                }, indent=2)

            # Check for answer
            answer = get_answer(PROJECT_DIR, question_id)
            if answer is not None:
                # Check if user skipped
                if answer == "[SKIPPED]":
                    return json.dumps({
                        "skipped": True,
                        "message": "User skipped this question",
                        "question_id": question_id,
                    }, indent=2)

                print(f"[ASK_USER] Received answer: {answer}", file=sys.stderr)
                return json.dumps({
                    "answer": answer,
                    "question_id": question_id,
                }, indent=2)

            time.sleep(poll_interval)

    except Exception as e:
        return json.dumps({
            "error": "exception",
            "message": str(e),
        }, indent=2)


@mcp.tool()
def validate_code_quality(
    path: Annotated[Optional[str], Field(default=None, description="Specific file or directory to validate (relative to project). If not specified, validates entire project.")] = None,
) -> str:
    """Validate code for quality issues, security vulnerabilities, and placeholders.

    IMPORTANT: Run this tool before marking any feature as passing.

    This tool checks for:
    1. Mock/fake data patterns (FORBIDDEN - must use real data)
    2. Placeholder/stub code (TODO, FIXME, NotImplementedError)
    3. Security vulnerabilities (OWASP Top 10 compliance)
    4. Legitimate placeholders that need documentation (API keys, secrets)

    The tool will:
    - Return PASS if no critical/high severity issues found
    - Return FAIL with list of blocking issues to fix
    - Generate PLACEHOLDERS.md documenting config values to replace

    Args:
        path: Optional specific path to validate. If omitted, validates entire project.

    Returns:
        JSON with validation results:
        - passes: bool (True if code is production-ready)
        - total_issues: Number of issues found
        - blocking_issues: Critical/high issues that must be fixed
        - placeholder_document: Path to generated PLACEHOLDERS.md if applicable
    """
    try:
        target_path = PROJECT_DIR
        if path:
            target_path = PROJECT_DIR / path
            if not target_path.exists():
                return json.dumps({
                    "error": f"Path does not exist: {path}",
                    "passes": False,
                }, indent=2)

        # Validate the target
        if target_path.is_file():
            from server.services.code_validator import scan_file, generate_validation_report
            issues, placeholders = scan_file(target_path)
            report = generate_validation_report(PROJECT_DIR, issues, placeholders)
            result = {
                'passes': report['passes'],
                'file': str(path),
                'issues': [
                    {
                        'severity': i.severity,
                        'category': i.category,
                        'line': i.line_number,
                        'message': i.message,
                        'owasp': i.owasp_category,
                    }
                    for i in issues
                ],
                'report': report,
            }
        else:
            result = validate_project(target_path)

        # Log summary
        if result['passes']:
            print(f"[VALIDATE] ✓ Code validation PASSED", file=sys.stderr)
        else:
            print(f"[VALIDATE] ✗ Code validation FAILED - {result.get('report', {}).get('total_issues', 0)} issues found", file=sys.stderr)

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "passes": False,
        }, indent=2)


@mcp.tool()
def get_security_checklist() -> str:
    """Get OWASP Top 10 security checklist for code review.

    Returns a checklist of security items to verify before marking features as passing.
    Use this as a reference when implementing authentication, authorization, data handling,
    or any security-sensitive functionality.

    Returns:
        JSON with OWASP Top 10 (2021) checklist items and verification steps.
    """
    checklist = {
        "title": "OWASP Top 10 Security Checklist (2021)",
        "instructions": "Verify each applicable item before marking feature as passing",
        "categories": [
            {
                "id": "A01:2021",
                "name": "Broken Access Control",
                "checks": [
                    "Deny access by default (whitelist approach)",
                    "Enforce record ownership - users can only access their own data",
                    "Disable directory listing on web servers",
                    "Log access control failures and alert on repeated failures",
                    "Rate limit API access to minimize automated attacks",
                    "Invalidate JWT tokens on server after logout",
                    "Use CORS restrictively (not * for origin)",
                ],
            },
            {
                "id": "A02:2021",
                "name": "Cryptographic Failures",
                "checks": [
                    "Classify data by sensitivity and apply controls accordingly",
                    "Don't store sensitive data unnecessarily",
                    "Encrypt all sensitive data at rest",
                    "Use strong, up-to-date algorithms (AES, RSA, SHA-256+)",
                    "Encrypt all data in transit with TLS",
                    "Disable caching for sensitive data responses",
                    "Use proper key management (don't hardcode keys)",
                    "Use bcrypt/scrypt/argon2 for password storage",
                ],
            },
            {
                "id": "A03:2021",
                "name": "Injection",
                "checks": [
                    "Use parameterized queries / prepared statements for SQL",
                    "Use ORM safely - avoid raw queries with user input",
                    "Escape special characters in user input",
                    "Validate and sanitize all user inputs",
                    "Use allowlists for input validation where possible",
                    "Avoid eval(), innerHTML, and similar dangerous functions",
                    "Use Content Security Policy (CSP) headers",
                ],
            },
            {
                "id": "A04:2021",
                "name": "Insecure Design",
                "checks": [
                    "Use threat modeling for critical flows",
                    "Implement proper error handling without exposing internals",
                    "Use secure design patterns (defense in depth)",
                    "Limit resource consumption (rate limiting, quotas)",
                    "Segregate tenant data in multi-tenant applications",
                ],
            },
            {
                "id": "A05:2021",
                "name": "Security Misconfiguration",
                "checks": [
                    "Remove or disable unnecessary features/frameworks",
                    "Disable debug mode in production",
                    "Configure proper security headers (X-Frame-Options, etc.)",
                    "Keep all software/dependencies up to date",
                    "Use secure defaults for all configurations",
                    "Don't expose stack traces or detailed errors to users",
                ],
            },
            {
                "id": "A06:2021",
                "name": "Vulnerable Components",
                "checks": [
                    "Remove unused dependencies",
                    "Continuously monitor for vulnerabilities (npm audit, etc.)",
                    "Only use components from official sources",
                    "Keep components up to date with security patches",
                    "Use lockfiles (package-lock.json, yarn.lock)",
                ],
            },
            {
                "id": "A07:2021",
                "name": "Identification and Authentication Failures",
                "checks": [
                    "Implement multi-factor authentication where possible",
                    "Don't ship with default credentials",
                    "Implement weak password checks",
                    "Use secure password recovery mechanisms",
                    "Limit failed login attempts (account lockout/delays)",
                    "Use secure session management (random IDs, proper expiry)",
                    "Invalidate sessions on logout",
                ],
            },
            {
                "id": "A08:2021",
                "name": "Software and Data Integrity Failures",
                "checks": [
                    "Use digital signatures to verify software/data integrity",
                    "Use npm/pip with lockfiles for reproducible builds",
                    "Review code changes (no automatic merging of untrusted code)",
                    "Ensure CI/CD pipeline has proper access controls",
                    "Validate serialized data (don't deserialize untrusted data)",
                ],
            },
            {
                "id": "A09:2021",
                "name": "Security Logging and Monitoring Failures",
                "checks": [
                    "Log all authentication attempts (success and failure)",
                    "Log access control failures",
                    "Log input validation failures",
                    "Ensure logs contain enough context for forensics",
                    "Don't log sensitive data (passwords, tokens, PII)",
                    "Set up alerting for suspicious activities",
                    "Have an incident response plan",
                ],
            },
            {
                "id": "A10:2021",
                "name": "Server-Side Request Forgery (SSRF)",
                "checks": [
                    "Sanitize and validate all user-supplied URLs",
                    "Use allowlists for allowed URL schemas and destinations",
                    "Don't send raw responses to clients",
                    "Disable HTTP redirections",
                    "Use network segmentation to limit SSRF impact",
                ],
            },
        ],
    }

    return json.dumps(checklist, indent=2)


@mcp.tool()
def generate_placeholder_docs() -> str:
    """Generate documentation for all configuration placeholders in the project.

    Scans the project for legitimate placeholders (API keys, secrets, URLs that need
    to be configured) and generates a PLACEHOLDERS.md file documenting what needs
    to be replaced before deployment.

    This is different from code validation - these are EXPECTED placeholders for
    configuration values that vary by environment.

    Returns:
        JSON with:
        - document_path: Path to generated PLACEHOLDERS.md
        - placeholder_count: Number of placeholders found
        - by_type: Count of placeholders by type
    """
    try:
        from server.services.code_validator import scan_directory, generate_placeholder_document

        issues, placeholders = scan_directory(PROJECT_DIR)

        if not placeholders:
            return json.dumps({
                "message": "No configuration placeholders found",
                "placeholder_count": 0,
            }, indent=2)

        doc_path = generate_placeholder_document(PROJECT_DIR, placeholders)

        # Count by type
        by_type: dict[str, int] = {}
        for p in placeholders:
            by_type[p.placeholder_type] = by_type.get(p.placeholder_type, 0) + 1

        return json.dumps({
            "document_path": str(doc_path),
            "placeholder_count": len(placeholders),
            "by_type": by_type,
            "message": f"Generated {doc_path.name} with {len(placeholders)} placeholders to configure",
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e),
        }, indent=2)


@mcp.tool()
def generate_technical_docs() -> str:
    """Generate comprehensive technical documentation for the project.

    Creates a TECHNICAL_DOCS.md file with:
    - Architecture overview (tech stack, languages, frameworks)
    - Directory structure
    - Component/module documentation
    - API reference
    - Dependencies list
    - Configuration guide
    - Development instructions

    Call this tool when:
    - Project is complete (all features passing)
    - Major milestone reached
    - Before handoff to other developers
    - When comprehensive documentation is needed

    Returns:
        JSON with:
        - document_path: Path to generated TECHNICAL_DOCS.md
        - summary: Brief summary of what was documented
        - stats: Project statistics (files, lines, languages)
    """
    try:
        # Generate the documentation
        doc_content, doc_path = generate_technical_documentation(PROJECT_DIR)

        # Get project stats
        structure = analyze_project_structure(PROJECT_DIR)

        return json.dumps({
            "document_path": str(doc_path),
            "summary": f"Generated technical documentation for {PROJECT_DIR.name}",
            "stats": {
                "total_files": structure['file_count'],
                "total_lines": structure['line_count'],
                "languages": structure['languages'],
                "frameworks": structure['frameworks'],
                "directories": len(structure['directories']),
            },
            "sections": [
                "Architecture Overview",
                "Directory Structure",
                "Components & Modules",
                "API Reference",
                "Dependencies",
                "Configuration",
                "Development Guide",
            ],
            "message": f"Technical documentation generated at {doc_path.name}",
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e),
        }, indent=2)


if __name__ == "__main__":
    mcp.run()
