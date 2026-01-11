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

    Returns the feature with the lowest priority number that has passes=false.
    Use this at the start of each coding session to determine what to implement next.

    Returns:
        JSON with feature details (id, priority, category, name, description, steps, passes, in_progress)
        or error message if all features are passing.
    """
    session = get_session()
    try:
        feature = (
            session.query(Feature)
            .filter(Feature.passes == False)
            .order_by(Feature.priority.asc(), Feature.id.asc())
            .first()
        )

        if feature is None:
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

        return json.dumps(feature.to_dict(), indent=2)
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
