#!/usr/bin/env python3
"""
MCP Server for Agent Control
=============================

Provides tools to control the coding agent from the assistant chat.
Communicates with the FastAPI server via HTTP requests.

Tools:
- agent_get_status: Get current agent status
- agent_start: Start the agent
- agent_stop: Stop the agent
- agent_pause: Pause the agent
- agent_resume: Resume a paused agent
- agent_skip_feature: Skip the current feature
- agent_clear_stuck: Clear a stuck feature
- agent_inject_context: Add context for the agent's next session
- agent_get_progress: Get detailed progress information
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Configuration from environment
PROJECT_NAME = os.environ.get("PROJECT_NAME", "")
PROJECT_DIR = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8888")

# Initialize the MCP server
mcp = FastMCP("agent-control")


def _api_request(method: str, endpoint: str, data: dict | None = None) -> dict:
    """Make an HTTP request to the FastAPI server."""
    url = f"{API_BASE_URL}{endpoint}"

    headers = {"Content-Type": "application/json"}

    if data is not None:
        body = json.dumps(data).encode("utf-8")
    else:
        body = None

    try:
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        try:
            return {"error": json.loads(error_body).get("detail", error_body)}
        except json.JSONDecodeError:
            return {"error": error_body}
    except urllib.error.URLError as e:
        return {"error": f"Cannot connect to API server: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def agent_get_status() -> str:
    """Get the current status of the coding agent.

    Returns information about whether the agent is running, paused, stopped, or crashed.
    Also includes the process ID, start time, and current mode.

    Returns:
        JSON with: status (str), pid (int|null), started_at (str|null),
                   yolo_mode (bool), model (str|null)
    """
    if not PROJECT_NAME:
        return json.dumps({"error": "PROJECT_NAME not set"})

    result = _api_request("GET", f"/api/projects/{PROJECT_NAME}/agent/status")
    return json.dumps(result, indent=2)


@mcp.tool()
def agent_start(
    yolo_mode: Annotated[bool, Field(default=False, description="Enable YOLO mode (skip browser testing)")] = False,
    model: Annotated[str | None, Field(default=None, description="Model to use (e.g., claude-opus-4-5-20251101)")] = None
) -> str:
    """Start the coding agent.

    Launches the autonomous coding agent as a subprocess. The agent will
    begin implementing features from the queue.

    Args:
        yolo_mode: If True, skip browser testing for faster iteration
        model: Specific model to use (optional)

    Returns:
        JSON with: success (bool), message (str), pid (int) if successful
    """
    if not PROJECT_NAME:
        return json.dumps({"error": "PROJECT_NAME not set"})

    data = {"yolo_mode": yolo_mode}
    if model:
        data["model"] = model

    result = _api_request("POST", f"/api/projects/{PROJECT_NAME}/agent/start", data)
    return json.dumps(result, indent=2)


@mcp.tool()
def agent_stop() -> str:
    """Stop the coding agent.

    Gracefully terminates the agent subprocess. Use this to halt the agent
    before it completes all features.

    Returns:
        JSON with: success (bool), message (str)
    """
    if not PROJECT_NAME:
        return json.dumps({"error": "PROJECT_NAME not set"})

    result = _api_request("POST", f"/api/projects/{PROJECT_NAME}/agent/stop")
    return json.dumps(result, indent=2)


@mcp.tool()
def agent_pause() -> str:
    """Pause the coding agent.

    Suspends the agent process without terminating it. The agent can be
    resumed later to continue from where it left off.

    Returns:
        JSON with: success (bool), message (str)
    """
    if not PROJECT_NAME:
        return json.dumps({"error": "PROJECT_NAME not set"})

    result = _api_request("POST", f"/api/projects/{PROJECT_NAME}/agent/pause")
    return json.dumps(result, indent=2)


@mcp.tool()
def agent_resume() -> str:
    """Resume a paused coding agent.

    Continues the agent process from where it was paused.

    Returns:
        JSON with: success (bool), message (str)
    """
    if not PROJECT_NAME:
        return json.dumps({"error": "PROJECT_NAME not set"})

    result = _api_request("POST", f"/api/projects/{PROJECT_NAME}/agent/resume")
    return json.dumps(result, indent=2)


@mcp.tool()
def agent_skip_feature(
    feature_id: Annotated[int, Field(description="ID of the feature to skip", ge=1)]
) -> str:
    """Skip a feature that's blocking progress.

    Moves the specified feature to the end of the queue so the agent can
    work on other features first. Use this when:
    - A feature has dependencies that aren't implemented yet
    - The agent is stuck on a difficult feature
    - You want to prioritize other work

    Args:
        feature_id: The ID of the feature to skip

    Returns:
        JSON with skip result or error
    """
    if not PROJECT_NAME:
        return json.dumps({"error": "PROJECT_NAME not set"})

    result = _api_request("PATCH", f"/api/projects/{PROJECT_NAME}/features/{feature_id}/skip")
    return json.dumps(result, indent=2)


@mcp.tool()
def agent_clear_stuck(
    feature_id: Annotated[int, Field(description="ID of the feature to unstick", ge=1)]
) -> str:
    """Clear the in-progress status of a stuck feature.

    If the agent crashed or was stopped while working on a feature, that
    feature may be stuck in "in_progress" status. This tool clears that
    status so the feature returns to the pending queue.

    Args:
        feature_id: The ID of the stuck feature

    Returns:
        JSON with the updated feature or error
    """
    if not PROJECT_NAME:
        return json.dumps({"error": "PROJECT_NAME not set"})

    result = _api_request("PATCH", f"/api/projects/{PROJECT_NAME}/features/{feature_id}/clear-in-progress")
    return json.dumps(result, indent=2)


@mcp.tool()
def agent_inject_context(
    context: Annotated[str, Field(description="Context or instructions to add for the agent")]
) -> str:
    """Inject context or instructions for the agent's next session.

    Writes context to a special file that the agent reads at the start
    of each session. Use this to:
    - Provide hints about how to implement a feature
    - Share information the agent might need
    - Give specific instructions for the next task

    The context is appended to any existing context, so you can add
    multiple pieces of information.

    Args:
        context: The context or instructions to inject

    Returns:
        JSON with: success (bool), message (str)
    """
    if not PROJECT_DIR:
        return json.dumps({"error": "PROJECT_DIR not set"})

    context_file = PROJECT_DIR / ".agent_context.md"

    try:
        # Append to existing context
        existing = ""
        if context_file.exists():
            existing = context_file.read_text(encoding="utf-8")

        # Add separator if there's existing content
        if existing and not existing.endswith("\n\n"):
            existing += "\n\n"

        # Add timestamp and new context
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_content = f"{existing}---\n**Added at {timestamp}:**\n\n{context}\n"

        context_file.write_text(new_content, encoding="utf-8")

        return json.dumps({
            "success": True,
            "message": f"Context injected successfully. The agent will see this in its next session.",
            "file": str(context_file)
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to inject context: {e}"})


@mcp.tool()
def agent_clear_context() -> str:
    """Clear all injected context.

    Removes the context file so the agent starts fresh without any
    injected instructions.

    Returns:
        JSON with: success (bool), message (str)
    """
    if not PROJECT_DIR:
        return json.dumps({"error": "PROJECT_DIR not set"})

    context_file = PROJECT_DIR / ".agent_context.md"

    try:
        if context_file.exists():
            context_file.unlink()
            return json.dumps({
                "success": True,
                "message": "Context cleared successfully."
            }, indent=2)
        else:
            return json.dumps({
                "success": True,
                "message": "No context file found (already clear)."
            }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to clear context: {e}"})


@mcp.tool()
def agent_get_context() -> str:
    """View the currently injected context.

    Returns the contents of the context file that the agent will read
    in its next session.

    Returns:
        JSON with: has_context (bool), content (str|null)
    """
    if not PROJECT_DIR:
        return json.dumps({"error": "PROJECT_DIR not set"})

    context_file = PROJECT_DIR / ".agent_context.md"

    try:
        if context_file.exists():
            content = context_file.read_text(encoding="utf-8")
            return json.dumps({
                "has_context": True,
                "content": content
            }, indent=2)
        else:
            return json.dumps({
                "has_context": False,
                "content": None
            }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read context: {e}"})


@mcp.tool()
def agent_get_progress() -> str:
    """Get detailed progress information.

    Returns comprehensive statistics about feature completion, including
    counts by status, completion percentage, and any stuck features.

    Returns:
        JSON with: passing (int), in_progress (int), pending (int),
                   total (int), percentage (float), stuck_features (list)
    """
    if not PROJECT_NAME:
        return json.dumps({"error": "PROJECT_NAME not set"})

    # Get basic stats - returns {pending: [], in_progress: [], done: []}
    stats_result = _api_request("GET", f"/api/projects/{PROJECT_NAME}/features")

    if "error" in stats_result:
        return json.dumps(stats_result, indent=2)

    # Extract lists from response
    pending_list = stats_result.get("pending", [])
    in_progress_list = stats_result.get("in_progress", [])
    done_list = stats_result.get("done", [])

    pending = len(pending_list)
    in_progress = len(in_progress_list)
    passing = len(done_list)
    total = pending + in_progress + passing

    # Find stuck features (features that are in_progress)
    stuck_features = [
        {"id": f.get("id"), "name": f.get("name")}
        for f in in_progress_list
    ]

    result = {
        "passing": passing,
        "in_progress": in_progress,
        "pending": pending,
        "total": total,
        "percentage": round((passing / total) * 100, 1) if total > 0 else 0.0,
        "stuck_features": stuck_features
    }

    return json.dumps(result, indent=2)


@mcp.tool()
def agent_reset_stuck_detection() -> str:
    """Reset the stuck detection tracking.

    Clears the feature attempt counts so the agent can retry features
    that were previously marked as stuck. Use this after fixing issues
    that were causing features to fail.

    Returns:
        JSON with: success (bool), message (str)
    """
    if not PROJECT_DIR:
        return json.dumps({"error": "PROJECT_DIR not set"})

    attempts_file = PROJECT_DIR / ".feature_attempts"

    try:
        if attempts_file.exists():
            attempts_file.unlink()
            return json.dumps({
                "success": True,
                "message": "Stuck detection reset. All feature attempt counts cleared."
            }, indent=2)
        else:
            return json.dumps({
                "success": True,
                "message": "No stuck detection data found (already clear)."
            }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to reset stuck detection: {e}"})


if __name__ == "__main__":
    mcp.run()
