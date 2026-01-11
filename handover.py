"""
Session Handover Notes
======================

Generates and manages handover notes between agent sessions.
When a session ends (max_sessions reached, stopped, etc.), handover notes
are generated to help the next session pick up where it left off.

Handover notes include:
- Progress summary (features passing/remaining)
- Current feature being worked on
- Recent activity summary
- Any stuck features or issues
- Recommendations for next session
"""

import json
from datetime import datetime
from pathlib import Path

from progress import count_passing_tests, get_feature_attempts, get_current_feature_id
from usage_tracking import load_usage_stats


HANDOVER_FILE = ".agent_handover.md"


def get_feature_details(project_dir: Path) -> dict:
    """Get details about features for handover notes."""
    import sqlite3

    db_file = project_dir / "features.db"
    if not db_file.exists():
        return {"pending": [], "in_progress": [], "passing": [], "total": 0}

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get pending features (not passing, not in progress)
        cursor.execute("""
            SELECT id, name, category FROM features
            WHERE passes = 0 AND (in_progress = 0 OR in_progress IS NULL)
            ORDER BY priority ASC LIMIT 5
        """)
        pending = [{"id": r[0], "name": r[1], "category": r[2]} for r in cursor.fetchall()]

        # Get in-progress features
        cursor.execute("""
            SELECT id, name, category FROM features
            WHERE in_progress = 1
        """)
        in_progress = [{"id": r[0], "name": r[1], "category": r[2]} for r in cursor.fetchall()]

        # Get recently passed features (last 5)
        cursor.execute("""
            SELECT id, name, category FROM features
            WHERE passes = 1
            ORDER BY id DESC LIMIT 5
        """)
        recent_passing = [{"id": r[0], "name": r[1], "category": r[2]} for r in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) FROM features")
        total = cursor.fetchone()[0]

        conn.close()

        return {
            "pending": pending,
            "in_progress": in_progress,
            "recent_passing": recent_passing,
            "total": total
        }
    except Exception:
        return {"pending": [], "in_progress": [], "recent_passing": [], "total": 0}


def generate_handover_notes(
    project_dir: Path,
    reason: str,
    session_count: int,
) -> str:
    """
    Generate handover notes for the next session.

    Args:
        project_dir: Project directory
        reason: Why the session ended (e.g., "max_sessions reached", "all features complete")
        session_count: Number of sessions that ran

    Returns:
        The generated handover notes as markdown
    """
    passing, in_progress_count, total = count_passing_tests(project_dir)
    feature_details = get_feature_details(project_dir)
    attempts = get_feature_attempts(project_dir)
    usage = load_usage_stats(project_dir)
    current_feature = get_current_feature_id(project_dir)

    # Calculate progress
    percentage = (passing / total * 100) if total > 0 else 0
    remaining = total - passing

    # Build handover notes
    notes = f"""# Agent Handover Notes

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Session ended: {reason}

## Progress Summary

- **Features Passing**: {passing}/{total} ({percentage:.1f}%)
- **Features Remaining**: {remaining}
- **Sessions Completed**: {session_count}
- **Total Cost**: ${usage.total_cost_usd:.4f}
- **Total Tokens**: {usage.total_tokens:,}

"""

    # Current work
    if feature_details["in_progress"]:
        notes += "## Currently In Progress\n\n"
        for f in feature_details["in_progress"]:
            attempt_count = attempts.get(str(f["id"]), 0)
            notes += f"- **{f['category']}: {f['name']}** (ID: {f['id']})"
            if attempt_count > 0:
                notes += f" - {attempt_count} attempt(s)"
            notes += "\n"
        notes += "\n"

    # Stuck features
    stuck = [(fid, count) for fid, count in attempts.items() if count >= 2]
    if stuck:
        notes += "## Potentially Stuck Features\n\n"
        notes += "These features have been attempted multiple times without success:\n\n"
        for fid, count in stuck:
            # Try to get feature name
            for f in feature_details.get("pending", []) + feature_details.get("in_progress", []):
                if str(f["id"]) == fid:
                    notes += f"- **{f['name']}** (ID: {fid}) - {count} attempts\n"
                    break
            else:
                notes += f"- Feature ID {fid} - {count} attempts\n"
        notes += "\n"
        notes += "**Recommendation**: Consider using `feature_skip` to move past these, or investigate why they're failing.\n\n"

    # Next up
    if feature_details["pending"]:
        notes += "## Next Features to Implement\n\n"
        for f in feature_details["pending"][:5]:
            notes += f"- {f['category']}: {f['name']} (ID: {f['id']})\n"
        notes += "\n"

    # Recent successes
    if feature_details["recent_passing"]:
        notes += "## Recently Completed\n\n"
        for f in feature_details["recent_passing"]:
            notes += f"- {f['category']}: {f['name']}\n"
        notes += "\n"

    # Session stats
    if usage.total_sessions > 0:
        avg_cost = usage.total_cost_usd / usage.total_sessions
        avg_duration = usage.total_duration_ms / usage.total_sessions / 1000
        notes += f"""## Session Statistics

- Average cost per session: ${avg_cost:.4f}
- Average duration per session: {avg_duration:.1f}s
- Total API time: {usage.total_duration_ms / 1000:.1f}s

"""

    # Recommendations
    notes += "## Recommendations for Next Session\n\n"

    if stuck:
        notes += "1. Review stuck features - they may have unclear requirements or dependencies\n"

    if in_progress_count > 0:
        notes += f"2. A feature is currently in progress - the agent will continue from there\n"
    else:
        notes += f"2. Start with the next pending feature in the queue\n"

    if percentage < 50:
        notes += "3. Focus on core functionality first before edge cases\n"
    elif percentage < 90:
        notes += "3. Good progress! Continue implementing remaining features\n"
    else:
        notes += "3. Almost done! Focus on the final features and polish\n"

    return notes


def save_handover_notes(project_dir: Path, notes: str) -> Path:
    """Save handover notes to file."""
    handover_file = project_dir / HANDOVER_FILE
    handover_file.write_text(notes, encoding="utf-8")
    return handover_file


def load_handover_notes(project_dir: Path) -> str | None:
    """Load handover notes if they exist."""
    handover_file = project_dir / HANDOVER_FILE
    if not handover_file.exists():
        return None

    try:
        return handover_file.read_text(encoding="utf-8")
    except (OSError, PermissionError):
        return None


def clear_handover_notes(project_dir: Path) -> None:
    """Clear handover notes after they've been used."""
    handover_file = project_dir / HANDOVER_FILE
    if handover_file.exists():
        handover_file.unlink()


def create_handover_on_exit(
    project_dir: Path,
    reason: str,
    session_count: int,
) -> Path:
    """
    Create handover notes when a session ends.

    Args:
        project_dir: Project directory
        reason: Why the session ended
        session_count: Number of sessions completed

    Returns:
        Path to the handover file
    """
    notes = generate_handover_notes(project_dir, reason, session_count)
    path = save_handover_notes(project_dir, notes)
    print(f"\nHandover notes saved to: {path}")
    return path
