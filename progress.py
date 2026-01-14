"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
Uses direct SQLite access for database queries.
Includes comprehensive webhook notifications for milestones and usage warnings.
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

# Milestone percentages to notify on
MILESTONE_PERCENTAGES = [25, 50, 75, 100]

# Usage warning thresholds (percentage of limit used)
USAGE_WARNING_THRESHOLDS = [75, 90, 95, 100]

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


def _send_webhook(payload: dict) -> bool:
    """Send a webhook notification. Returns True if successful."""
    if not WEBHOOK_URL:
        return False

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps([payload]).encode("utf-8"),  # n8n expects array
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        print(f"[Webhook notification failed: {e}]")
        return False


def _get_milestone_reached(current_pct: float, previous_pct: float) -> int | None:
    """Check if a milestone was just crossed. Returns the milestone or None."""
    for milestone in MILESTONE_PERCENTAGES:
        if previous_pct < milestone <= current_pct:
            return milestone
    return None


def _get_milestone_message(milestone: int, passing: int, total: int) -> str:
    """Get a human-readable milestone message."""
    messages = {
        25: f"Quarter way there! {passing}/{total} features complete.",
        50: f"Halfway done! {passing}/{total} features complete.",
        75: f"Three quarters complete! {passing}/{total} features - almost there!",
        100: f"All {total} features complete! Project finished successfully.",
    }
    return messages.get(milestone, f"{milestone}% complete: {passing}/{total} features.")


def send_progress_webhook(passing: int, total: int, project_dir: Path) -> None:
    """
    Send comprehensive webhook notification when progress changes.

    Notifications include:
    - Progress updates (when features complete)
    - Milestone alerts (25%, 50%, 75%, 100%)
    - Completion notification
    """
    if not WEBHOOK_URL:
        return  # Webhook not configured

    cache_file = project_dir / PROGRESS_CACHE_FILE
    previous = 0
    previous_passing_ids = set()
    notified_milestones = []

    # Read previous progress and passing feature IDs
    if cache_file.exists():
        try:
            cache_data = json.loads(cache_file.read_text())
            previous = cache_data.get("count", 0)
            previous_passing_ids = set(cache_data.get("passing_ids", []))
            notified_milestones = cache_data.get("notified_milestones", [])
        except Exception:
            previous = 0

    # Calculate percentages
    current_pct = round((passing / total) * 100, 1) if total > 0 else 0
    previous_pct = round((previous / total) * 100, 1) if total > 0 else 0

    # Only notify if progress increased
    if passing > previous:
        # Find which features are now passing
        completed_tests = []
        current_passing_ids = []

        # Detect transition from old cache format
        is_old_cache_format = len(previous_passing_ids) == 0 and previous > 0

        # Get all passing features via direct database access
        all_passing = get_all_passing_features(project_dir)
        for feature in all_passing:
            feature_id = feature.get("id")
            current_passing_ids.append(feature_id)
            if not is_old_cache_format and feature_id not in previous_passing_ids:
                name = feature.get("name", f"Feature #{feature_id}")
                category = feature.get("category", "")
                if category:
                    completed_tests.append(f"{category}: {name}")
                else:
                    completed_tests.append(name)

        # Check for milestone
        milestone = _get_milestone_reached(current_pct, previous_pct)
        is_milestone = milestone is not None and milestone not in notified_milestones
        is_complete = passing == total

        # Determine event type and priority
        if is_complete:
            event_type = "project_complete"
            priority = "high"
            title = "Project Complete!"
            message = _get_milestone_message(100, passing, total)
        elif is_milestone:
            event_type = "milestone_reached"
            priority = "medium"
            title = f"{milestone}% Milestone Reached"
            message = _get_milestone_message(milestone, passing, total)
            notified_milestones.append(milestone)
        else:
            event_type = "progress_update"
            priority = "low"
            title = "Progress Update"
            message = f"{passing}/{total} features complete ({current_pct}%)"

        # Build comprehensive payload
        payload = {
            "event": event_type,
            "priority": priority,
            "title": title,
            "message": message,
            "project": project_dir.name,
            "progress": {
                "passing": passing,
                "total": total,
                "percentage": current_pct,
                "remaining": total - passing,
            },
            "session": {
                "previous_passing": previous,
                "features_completed": passing - previous,
                "completed_features": completed_tests,
            },
            "milestone": {
                "reached": is_milestone,
                "value": milestone,
                "all_notified": notified_milestones,
            } if is_milestone else None,
            "estimates": {
                "features_remaining": total - passing,
                "estimated_time_min": (total - passing) * 3,
                "estimated_time_max": (total - passing) * 5,
            } if not is_complete else None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Remove None values for cleaner payload
        payload = {k: v for k, v in payload.items() if v is not None}

        _send_webhook(payload)

        # Update cache with count, passing IDs, and notified milestones
        cache_file.write_text(
            json.dumps({
                "count": passing,
                "passing_ids": current_passing_ids,
                "notified_milestones": notified_milestones,
            })
        )
    else:
        # Update cache even if no change (for initial state)
        if not cache_file.exists():
            all_passing = get_all_passing_features(project_dir)
            current_passing_ids = [f.get("id") for f in all_passing]
            cache_file.write_text(
                json.dumps({
                    "count": passing,
                    "passing_ids": current_passing_ids,
                    "notified_milestones": notified_milestones,
                })
            )


def send_usage_warning_webhook(
    project_dir: Path,
    usage_type: str,
    current_value: float,
    limit_value: float,
    unit: str = "",
) -> None:
    """
    Send webhook notification for usage warnings.

    Args:
        project_dir: Project directory
        usage_type: Type of usage (cost, tokens)
        current_value: Current usage value
        limit_value: Configured limit value
        unit: Unit string (e.g., "$", "tokens")
    """
    if not WEBHOOK_URL or limit_value <= 0:
        return

    cache_file = project_dir / PROGRESS_CACHE_FILE
    notified_usage_thresholds = {}

    # Read previous notifications
    if cache_file.exists():
        try:
            cache_data = json.loads(cache_file.read_text())
            notified_usage_thresholds = cache_data.get("notified_usage_thresholds", {})
        except Exception:
            pass

    # Calculate percentage used
    pct_used = (current_value / limit_value) * 100 if limit_value > 0 else 0

    # Check if we crossed a warning threshold
    previous_thresholds = notified_usage_thresholds.get(usage_type, [])
    threshold_reached = None

    for threshold in USAGE_WARNING_THRESHOLDS:
        if pct_used >= threshold and threshold not in previous_thresholds:
            threshold_reached = threshold
            previous_thresholds.append(threshold)
            break

    if threshold_reached is None:
        return  # No new threshold crossed

    # Determine severity
    if threshold_reached >= 100:
        severity = "critical"
        title = f"Usage Limit Exceeded: {usage_type.title()}"
        message = f"You have exceeded your {usage_type} limit!"
    elif threshold_reached >= 95:
        severity = "critical"
        title = f"Usage Critical: {usage_type.title()}"
        message = f"You have used {threshold_reached}% of your {usage_type} limit. Agent will stop soon."
    elif threshold_reached >= 90:
        severity = "warning"
        title = f"Usage Warning: {usage_type.title()}"
        message = f"You have used {threshold_reached}% of your {usage_type} limit."
    else:
        severity = "info"
        title = f"Usage Notice: {usage_type.title()}"
        message = f"You have used {threshold_reached}% of your {usage_type} limit."

    # Format values
    if unit == "$":
        current_str = f"${current_value:.2f}"
        limit_str = f"${limit_value:.2f}"
        remaining_str = f"${max(0, limit_value - current_value):.2f}"
    else:
        current_str = f"{int(current_value):,}"
        limit_str = f"{int(limit_value):,}"
        remaining_str = f"{int(max(0, limit_value - current_value)):,}"

    payload = {
        "event": "usage_warning",
        "priority": "high" if severity in ["critical", "warning"] else "medium",
        "severity": severity,
        "title": title,
        "message": message,
        "project": project_dir.name,
        "usage": {
            "type": usage_type,
            "current": current_value,
            "limit": limit_value,
            "remaining": max(0, limit_value - current_value),
            "percentage_used": round(pct_used, 1),
            "threshold_reached": threshold_reached,
            "formatted": {
                "current": current_str,
                "limit": limit_str,
                "remaining": remaining_str,
            },
        },
        "action_required": severity == "critical",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    _send_webhook(payload)

    # Update cache with notified thresholds
    try:
        cache_data = {}
        if cache_file.exists():
            cache_data = json.loads(cache_file.read_text())
        notified_usage_thresholds[usage_type] = previous_thresholds
        cache_data["notified_usage_thresholds"] = notified_usage_thresholds
        cache_file.write_text(json.dumps(cache_data))
    except Exception:
        pass


def send_agent_status_webhook(
    project_dir: Path,
    status: str,
    reason: str = "",
    details: dict | None = None,
) -> None:
    """
    Send webhook notification for agent status changes.

    Args:
        project_dir: Project directory
        status: Agent status (started, paused, stopped, stuck, error)
        reason: Reason for the status change
        details: Additional details
    """
    if not WEBHOOK_URL:
        return

    # Get current progress
    passing, in_progress, total = count_passing_tests(project_dir)
    percentage = round((passing / total) * 100, 1) if total > 0 else 0

    # Determine priority based on status
    priority_map = {
        "started": "low",
        "paused": "medium",
        "resumed": "low",
        "stopped": "medium",
        "stuck": "high",
        "error": "high",
        "complete": "high",
    }

    payload = {
        "event": "agent_status",
        "priority": priority_map.get(status, "medium"),
        "status": status,
        "reason": reason,
        "project": project_dir.name,
        "progress": {
            "passing": passing,
            "in_progress": in_progress,
            "total": total,
            "percentage": percentage,
        },
        "details": details,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    _send_webhook(payload)


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


def check_completion_status(project_dir: Path, allow_decomposition: bool = True) -> tuple[bool, str, str | None]:
    """
    Check if the agent should stop running or needs to decompose a feature.

    Args:
        project_dir: Project directory
        allow_decomposition: If True, stuck features trigger decomposition instead of stopping

    Returns:
        (should_stop, reason, action) tuple where:
        - should_stop: True if agent should terminate
        - reason: Human-readable explanation
        - action: "complete" | "stuck" | "decompose" | None
    """
    passing, in_progress, total = count_passing_tests(project_dir)

    # All features complete
    if total > 0 and passing == total:
        return True, f"All {total} features are passing!", "complete"

    # Check for stuck detection
    is_stuck, stuck_reason = check_stuck_detection(project_dir)
    if is_stuck:
        if allow_decomposition:
            # Instead of stopping, trigger decomposition
            stuck_feature_id = get_stuck_feature_id(project_dir)
            if stuck_feature_id:
                mark_feature_for_decomposition(project_dir, stuck_feature_id)
                return False, f"Feature #{stuck_feature_id} is stuck. Triggering decomposition.", "decompose"
        # Fall back to stopping if decomposition not allowed
        return True, stuck_reason, "stuck"

    return False, "", None


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


def get_stuck_feature_id(project_dir: Path) -> int | None:
    """
    Get the ID of a stuck feature (one that has reached max attempts).

    Returns:
        Feature ID if a feature is stuck, None otherwise.
    """
    attempts_file = project_dir / STUCK_DETECTION_FILE

    if not attempts_file.exists():
        return None

    try:
        attempts = json.loads(attempts_file.read_text())

        for feature_id, count in attempts.items():
            if count >= MAX_FEATURE_ATTEMPTS:
                return int(feature_id)

        return None
    except Exception:
        return None


def get_stuck_feature_details(project_dir: Path) -> dict | None:
    """
    Get details about a stuck feature for decomposition.

    Returns:
        Dictionary with feature details or None if no stuck feature.
    """
    feature_id = get_stuck_feature_id(project_dir)
    if feature_id is None:
        return None

    db_file = project_dir / "features.db"
    if not db_file.exists():
        return None

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, category, name, description, steps FROM features WHERE id = ?",
            (feature_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            # Parse steps (stored as JSON)
            steps = row[4]
            if isinstance(steps, str):
                steps = json.loads(steps)

            return {
                "id": row[0],
                "category": row[1],
                "name": row[2],
                "description": row[3],
                "steps": steps,
                "attempts": get_feature_attempts(project_dir).get(str(feature_id), 0),
            }
        return None
    except Exception:
        return None


def mark_feature_for_decomposition(project_dir: Path, feature_id: int) -> None:
    """
    Mark a feature as needing decomposition (used to trigger decomposition prompt).

    Args:
        project_dir: Project directory
        feature_id: ID of the feature to decompose
    """
    decompose_file = project_dir / ".pending_decomposition"
    decompose_file.write_text(str(feature_id))


def get_pending_decomposition(project_dir: Path) -> int | None:
    """
    Get the feature ID pending decomposition, if any.

    Returns:
        Feature ID if decomposition is pending, None otherwise.
    """
    decompose_file = project_dir / ".pending_decomposition"
    if decompose_file.exists():
        try:
            return int(decompose_file.read_text().strip())
        except Exception:
            return None
    return None


def clear_pending_decomposition(project_dir: Path) -> None:
    """Clear the pending decomposition marker."""
    decompose_file = project_dir / ".pending_decomposition"
    if decompose_file.exists():
        decompose_file.unlink()


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
