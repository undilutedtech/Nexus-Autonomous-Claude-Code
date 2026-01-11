"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
Uses direct SQLite access for database queries.
"""

import json
import os
import sqlite3
import urllib.request
from datetime import datetime
from pathlib import Path

WEBHOOK_URL = os.environ.get("PROGRESS_N8N_WEBHOOK_URL")
PROGRESS_CACHE_FILE = ".progress_cache"
STUCK_DETECTION_FILE = ".feature_attempts"

# Configuration via environment variables
MAX_FEATURE_ATTEMPTS = int(os.environ.get("NEXUS_MAX_FEATURE_ATTEMPTS", "3"))
AUTO_CONTINUE_DELAY = int(os.environ.get("NEXUS_AUTO_CONTINUE_DELAY", "3"))

# Agent phase constants
PHASE_IDLE = "idle"
PHASE_INITIALIZING = "initializing"  # Reading spec, preparing environment
PHASE_CREATING_FEATURES = "creating_features"  # Generating feature test cases
PHASE_IMPLEMENTING = "implementing"  # Building features one by one
PHASE_COMPLETE = "complete"  # All features passing

# Estimated times for phases (in minutes)
PHASE_ESTIMATES = {
    PHASE_INITIALIZING: (5, 10),  # 5-10 minutes
    PHASE_CREATING_FEATURES: (10, 20),  # 10-20 minutes for ~200 features
    PHASE_IMPLEMENTING: None,  # Depends on feature count
}


def get_agent_phase(project_dir: Path, agent_running: bool = False) -> dict:
    """
    Detect the current phase of the agent based on project state.

    Args:
        project_dir: Directory containing the project
        agent_running: Whether the agent process is currently running

    Returns:
        Dictionary with phase info:
        - phase: Current phase name
        - description: Human-readable description
        - estimate_min: Minimum estimated time remaining (minutes)
        - estimate_max: Maximum estimated time remaining (minutes)
        - progress: Progress percentage (0-100) if applicable
        - features_total: Total feature count
        - features_passing: Passing feature count
    """
    # Check if project has app spec
    has_spec = (project_dir / "app_spec.txt").exists() or \
               (project_dir / "prompts" / "app_spec.txt").exists()

    # Get feature counts
    passing, in_progress, total = count_passing_tests(project_dir)

    # Determine phase
    # Check for completion first (works even when agent stopped)
    if passing == total and total > 0:
        phase = PHASE_COMPLETE
        description = f"All {total} features implemented successfully!"
        estimate_min, estimate_max = 0, 0
        progress = 100
    elif not agent_running:
        phase = PHASE_IDLE
        description = "Agent is not running"
        estimate_min, estimate_max = None, None
        progress = None
    elif total == 0:
        # No features yet - either initializing or creating features
        if not has_spec:
            phase = PHASE_IDLE
            description = "Waiting for app specification"
            estimate_min, estimate_max = None, None
            progress = None
        else:
            # Agent is running but no features - creating features
            phase = PHASE_CREATING_FEATURES
            description = "Analyzing app spec and generating test cases. This typically takes 10-20 minutes for a full application."
            estimate_min, estimate_max = PHASE_ESTIMATES[PHASE_CREATING_FEATURES]
            progress = None  # Can't estimate progress during feature creation
    else:
        phase = PHASE_IMPLEMENTING
        progress = (passing / total * 100) if total > 0 else 0
        remaining = total - passing
        # Estimate ~3-5 minutes per feature
        estimate_min = remaining * 3
        estimate_max = remaining * 5
        description = f"Implementing features: {passing}/{total} complete ({progress:.1f}%)"

    return {
        "phase": phase,
        "description": description,
        "estimate_min": estimate_min,
        "estimate_max": estimate_max,
        "progress": progress,
        "features_total": total,
        "features_passing": passing,
        "features_in_progress": in_progress,
    }


def has_features(project_dir: Path) -> bool:
    """
    Check if the project has features in the database.

    This is used to determine if the initializer agent needs to run.
    We check the database directly (not via API) since the API server
    may not be running yet when this check is performed.

    Returns True if:
    - features.db exists AND has at least 1 feature, OR
    - feature_list.json exists (legacy format)

    Returns False if no features exist (initializer needs to run).
    """
    import sqlite3

    # Check legacy JSON file first
    json_file = project_dir / "feature_list.json"
    if json_file.exists():
        return True

    # Check SQLite database
    db_file = project_dir / "features.db"
    if not db_file.exists():
        return False

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM features")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        # Database exists but can't be read or has no features table
        return False


def count_passing_tests(project_dir: Path) -> tuple[int, int, int]:
    """
    Count passing, in_progress, and total tests via direct database access.

    Args:
        project_dir: Directory containing the project

    Returns:
        (passing_count, in_progress_count, total_count)
    """
    db_file = project_dir / "features.db"
    if not db_file.exists():
        return 0, 0, 0

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM features")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM features WHERE passes = 1")
        passing = cursor.fetchone()[0]
        # Handle case where in_progress column doesn't exist yet
        try:
            cursor.execute("SELECT COUNT(*) FROM features WHERE in_progress = 1")
            in_progress = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            in_progress = 0
        conn.close()
        return passing, in_progress, total
    except Exception as e:
        print(f"[Database error in count_passing_tests: {e}]")
        return 0, 0, 0


def get_all_passing_features(project_dir: Path) -> list[dict]:
    """
    Get all passing features for webhook notifications.

    Args:
        project_dir: Directory containing the project

    Returns:
        List of dicts with id, category, name for each passing feature
    """
    db_file = project_dir / "features.db"
    if not db_file.exists():
        return []

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, category, name FROM features WHERE passes = 1 ORDER BY priority ASC"
        )
        features = [
            {"id": row[0], "category": row[1], "name": row[2]}
            for row in cursor.fetchall()
        ]
        conn.close()
        return features
    except Exception:
        return []


def send_progress_webhook(passing: int, total: int, project_dir: Path) -> None:
    """Send webhook notification when progress increases."""
    if not WEBHOOK_URL:
        return  # Webhook not configured

    cache_file = project_dir / PROGRESS_CACHE_FILE
    previous = 0
    previous_passing_ids = set()

    # Read previous progress and passing feature IDs
    if cache_file.exists():
        try:
            cache_data = json.loads(cache_file.read_text())
            previous = cache_data.get("count", 0)
            previous_passing_ids = set(cache_data.get("passing_ids", []))
        except Exception:
            previous = 0

    # Only notify if progress increased
    if passing > previous:
        # Find which features are now passing via API
        completed_tests = []
        current_passing_ids = []

        # Detect transition from old cache format (had count but no passing_ids)
        # In this case, we can't reliably identify which specific tests are new
        is_old_cache_format = len(previous_passing_ids) == 0 and previous > 0

        # Get all passing features via direct database access
        all_passing = get_all_passing_features(project_dir)
        for feature in all_passing:
            feature_id = feature.get("id")
            current_passing_ids.append(feature_id)
            # Only identify individual new tests if we have previous IDs to compare
            if not is_old_cache_format and feature_id not in previous_passing_ids:
                # This feature is newly passing
                name = feature.get("name", f"Feature #{feature_id}")
                category = feature.get("category", "")
                if category:
                    completed_tests.append(f"{category} {name}")
                else:
                    completed_tests.append(name)

        payload = {
            "event": "test_progress",
            "passing": passing,
            "total": total,
            "percentage": round((passing / total) * 100, 1) if total > 0 else 0,
            "previous_passing": previous,
            "tests_completed_this_session": passing - previous,
            "completed_tests": completed_tests,
            "project": project_dir.name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps([payload]).encode("utf-8"),  # n8n expects array
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            print(f"[Webhook notification failed: {e}]")

        # Update cache with count and passing IDs
        cache_file.write_text(
            json.dumps({"count": passing, "passing_ids": current_passing_ids})
        )
    else:
        # Update cache even if no change (for initial state)
        if not cache_file.exists():
            all_passing = get_all_passing_features(project_dir)
            current_passing_ids = [f.get("id") for f in all_passing]
            cache_file.write_text(
                json.dumps({"count": passing, "passing_ids": current_passing_ids})
            )


def print_session_header(
    session_num: int,
    is_initializer: bool,
    project_dir: Path | None = None,
) -> None:
    """Print a formatted header for the session with feature progress."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"

    print("\n" + "=" * 70)
    print(f"  SESSION {session_num}: {session_type}")

    # Show feature progress for coding sessions
    if not is_initializer and project_dir:
        passing, in_progress, total = count_passing_tests(project_dir)
        if total > 0:
            percentage = (passing / total) * 100
            remaining = total - passing
            progress_bar = _create_progress_bar(percentage, width=30)
            print(f"  {progress_bar} {passing}/{total} ({percentage:.1f}%)")
            if remaining > 0:
                print(f"  {remaining} features remaining")

    print("=" * 70)
    print()


def _create_progress_bar(percentage: float, width: int = 30) -> str:
    """Create a text-based progress bar."""
    filled = int(width * percentage / 100)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}]"


def print_progress_summary(project_dir: Path) -> None:
    """Print a summary of current progress."""
    passing, in_progress, total = count_passing_tests(project_dir)

    if total > 0:
        percentage = (passing / total) * 100
        status_parts = [f"{passing}/{total} tests passing ({percentage:.1f}%)"]
        if in_progress > 0:
            status_parts.append(f"{in_progress} in progress")
        print(f"\nProgress: {', '.join(status_parts)}")
        send_progress_webhook(passing, total, project_dir)
    else:
        print("\nProgress: No features in database yet")


def check_completion_status(project_dir: Path) -> tuple[bool, str]:
    """
    Check if the agent should stop running.

    Returns:
        (should_stop, reason) tuple where:
        - should_stop: True if agent should terminate
        - reason: Human-readable explanation
    """
    passing, in_progress, total = count_passing_tests(project_dir)

    # All features complete
    if total > 0 and passing == total:
        return True, f"All {total} features are passing!"

    # Check for stuck detection
    is_stuck, stuck_reason = check_stuck_detection(project_dir)
    if is_stuck:
        return True, stuck_reason

    return False, ""


def get_current_feature_id(project_dir: Path) -> int | None:
    """
    Get the ID of the feature currently in progress.

    Returns:
        Feature ID if one is in progress, None otherwise.
    """
    db_file = project_dir / "features.db"
    if not db_file.exists():
        return None

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM features WHERE in_progress = 1 LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def record_feature_attempt(project_dir: Path, feature_id: int) -> int:
    """
    Record an attempt at implementing a feature.

    Args:
        project_dir: Project directory
        feature_id: ID of the feature being attempted

    Returns:
        Number of attempts for this feature (including this one)
    """
    attempts_file = project_dir / STUCK_DETECTION_FILE

    # Load existing attempts
    attempts: dict[str, int] = {}
    if attempts_file.exists():
        try:
            attempts = json.loads(attempts_file.read_text())
        except Exception:
            attempts = {}

    # Increment attempt count
    key = str(feature_id)
    attempts[key] = attempts.get(key, 0) + 1

    # Save back
    attempts_file.write_text(json.dumps(attempts, indent=2))

    return attempts[key]


def clear_feature_attempt(project_dir: Path, feature_id: int) -> None:
    """
    Clear attempt count for a feature (called when feature passes).

    Args:
        project_dir: Project directory
        feature_id: ID of the feature that passed
    """
    attempts_file = project_dir / STUCK_DETECTION_FILE

    if not attempts_file.exists():
        return

    try:
        attempts = json.loads(attempts_file.read_text())
        key = str(feature_id)
        if key in attempts:
            del attempts[key]
            attempts_file.write_text(json.dumps(attempts, indent=2))
    except Exception:
        pass


def check_stuck_detection(project_dir: Path) -> tuple[bool, str]:
    """
    Check if the agent appears to be stuck on a feature.

    Returns:
        (is_stuck, reason) tuple
    """
    attempts_file = project_dir / STUCK_DETECTION_FILE

    if not attempts_file.exists():
        return False, ""

    try:
        attempts = json.loads(attempts_file.read_text())

        # Find any feature with too many attempts
        for feature_id, count in attempts.items():
            if count >= MAX_FEATURE_ATTEMPTS:
                return True, (
                    f"Feature #{feature_id} has been attempted {count} times "
                    f"(max: {MAX_FEATURE_ATTEMPTS}). Agent appears stuck. "
                    f"Consider using feature_skip to move past this feature."
                )

        return False, ""
    except Exception:
        return False, ""


def get_feature_attempts(project_dir: Path) -> dict[str, int]:
    """
    Get all feature attempt counts.

    Returns:
        Dict mapping feature ID (as string) to attempt count
    """
    attempts_file = project_dir / STUCK_DETECTION_FILE

    if not attempts_file.exists():
        return {}

    try:
        return json.loads(attempts_file.read_text())
    except Exception:
        return {}


def reset_stuck_detection(project_dir: Path) -> None:
    """
    Reset all stuck detection data (e.g., when starting fresh).

    Args:
        project_dir: Project directory
    """
    attempts_file = project_dir / STUCK_DETECTION_FILE
    if attempts_file.exists():
        attempts_file.unlink()
