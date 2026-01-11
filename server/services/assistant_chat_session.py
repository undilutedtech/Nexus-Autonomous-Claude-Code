"""
Assistant Chat Session
======================

Manages read-only conversational assistant sessions for projects.
The assistant can answer questions about the codebase and features
but cannot modify any files.
"""

import json
import logging
import os
import shutil
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Optional

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

from .assistant_database import (
    add_message,
    create_conversation,
)

logger = logging.getLogger(__name__)

# Root directory of the project
ROOT_DIR = Path(__file__).parent.parent.parent

# Read-only feature MCP tools (no mark_passing, create_bulk)
READONLY_FEATURE_MCP_TOOLS = [
    "mcp__features__feature_get_stats",
    "mcp__features__feature_get_next",
    "mcp__features__feature_get_for_regression",
    "mcp__features__feature_skip",  # Allow skipping features
    "mcp__features__feature_clear_in_progress",  # Allow clearing stuck features
]

# Agent control MCP tools
AGENT_CONTROL_MCP_TOOLS = [
    "mcp__agent-control__agent_get_status",
    "mcp__agent-control__agent_start",
    "mcp__agent-control__agent_stop",
    "mcp__agent-control__agent_pause",
    "mcp__agent-control__agent_resume",
    "mcp__agent-control__agent_skip_feature",
    "mcp__agent-control__agent_clear_stuck",
    "mcp__agent-control__agent_inject_context",
    "mcp__agent-control__agent_clear_context",
    "mcp__agent-control__agent_get_context",
    "mcp__agent-control__agent_get_progress",
    "mcp__agent-control__agent_reset_stuck_detection",
]

# Read-only built-in tools (no Write, Edit, Bash)
READONLY_BUILTIN_TOOLS = [
    "Read",
    "Glob",
    "Grep",
    "WebFetch",
    "WebSearch",
]


def get_system_prompt(project_name: str, project_dir: Path) -> str:
    """Generate the system prompt for the assistant with project context."""
    # Try to load app_spec.txt for context
    app_spec_content = ""
    app_spec_path = project_dir / "prompts" / "app_spec.txt"
    if app_spec_path.exists():
        try:
            app_spec_content = app_spec_path.read_text(encoding="utf-8")
            # Truncate if too long
            if len(app_spec_content) > 5000:
                app_spec_content = app_spec_content[:5000] + "\n... (truncated)"
        except Exception as e:
            logger.warning(f"Failed to read app_spec.txt: {e}")

    return f"""You are a helpful project assistant for the "{project_name}" project.

Your role is to help users understand the codebase, answer questions about features, explain how code works, AND control the coding agent. You can read files, search code, and manage the agent's execution.

## Your Capabilities

### File & Code Analysis (Read-Only)
- Read and analyze source code files
- Search for patterns in the codebase
- Look up documentation online
- Check feature progress and status

### Agent Control (Full Control)
- Start, stop, pause, and resume the coding agent
- Skip features that are blocking progress
- Clear stuck features from the in-progress queue
- Inject context and instructions for the agent
- Monitor agent progress and status
- Reset stuck detection when issues are resolved

## Project Specification

{app_spec_content if app_spec_content else "(No app specification found)"}

## Available Tools

### Code Analysis Tools
- **Read**: Read file contents
- **Glob**: Find files by pattern (e.g., "**/*.tsx")
- **Grep**: Search file contents with regex
- **WebFetch/WebSearch**: Look up documentation online

### Feature Tools
- **feature_get_stats**: Get feature completion progress
- **feature_get_next**: See the next pending feature
- **feature_get_for_regression**: See passing features
- **feature_skip**: Skip a feature to the end of the queue
- **feature_clear_in_progress**: Clear a stuck feature's status

### Agent Control Tools
- **agent_get_status**: Check if agent is running/paused/stopped
- **agent_start**: Start the coding agent (with optional YOLO mode)
- **agent_stop**: Stop the coding agent
- **agent_pause**: Pause the agent (can resume later)
- **agent_resume**: Resume a paused agent
- **agent_skip_feature**: Skip a problematic feature
- **agent_clear_stuck**: Clear in-progress status of a stuck feature
- **agent_inject_context**: Add context/instructions for the agent's next session
- **agent_clear_context**: Clear all injected context
- **agent_get_context**: View currently injected context
- **agent_get_progress**: Get detailed progress statistics
- **agent_reset_stuck_detection**: Reset attempt tracking for stuck features

## Guidelines

1. Be concise and helpful
2. When explaining code, reference specific file paths and line numbers
3. Use the feature tools to answer questions about project progress
4. Search the codebase to find relevant information before answering
5. If you're unsure, say so rather than guessing
6. When the user asks to control the agent, use the appropriate agent control tools
7. If a feature is stuck, consider using skip or clear-stuck to unblock progress
8. Use inject_context to provide helpful hints to the agent about difficult features"""


class AssistantChatSession:
    """
    Manages a read-only assistant conversation for a project.

    Uses Claude Opus 4.5 with only read-only tools enabled.
    Persists conversation history to SQLite.
    """

    def __init__(self, project_name: str, project_dir: Path, conversation_id: Optional[int] = None):
        """
        Initialize the session.

        Args:
            project_name: Name of the project
            project_dir: Absolute path to the project directory
            conversation_id: Optional existing conversation ID to resume
        """
        self.project_name = project_name
        self.project_dir = project_dir
        self.conversation_id = conversation_id
        self.client: Optional[ClaudeSDKClient] = None
        self._client_entered: bool = False
        self.created_at = datetime.now()

    async def close(self) -> None:
        """Clean up resources and close the Claude client."""
        if self.client and self._client_entered:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing Claude client: {e}")
            finally:
                self._client_entered = False
                self.client = None

    async def start(self) -> AsyncGenerator[dict, None]:
        """
        Initialize session with the Claude client.

        Creates a new conversation if none exists, then sends an initial greeting.
        Yields message chunks as they stream in.
        """
        # Create a new conversation if we don't have one
        if self.conversation_id is None:
            conv = create_conversation(self.project_dir, self.project_name)
            self.conversation_id = conv.id
            yield {"type": "conversation_created", "conversation_id": self.conversation_id}

        # Build permissions list for read-only file access + agent control
        permissions_list = [
            "Read(./**)",
            "Glob(./**)",
            "Grep(./**)",
            "WebFetch",
            "WebSearch",
            *READONLY_FEATURE_MCP_TOOLS,
            *AGENT_CONTROL_MCP_TOOLS,
        ]

        # Create security settings file
        security_settings = {
            "sandbox": {"enabled": False},  # No bash, so sandbox not needed
            "permissions": {
                "defaultMode": "bypassPermissions",  # Read-only + agent control
                "allow": permissions_list,
            },
        }
        settings_file = self.project_dir / ".claude_assistant_settings.json"
        with open(settings_file, "w") as f:
            json.dump(security_settings, f, indent=2)

        # Build MCP servers config - features MCP + agent control MCP
        mcp_servers = {
            "features": {
                "command": sys.executable,
                "args": ["-m", "mcp_server.feature_mcp"],
                "env": {
                    **os.environ,
                    "PROJECT_DIR": str(self.project_dir.resolve()),
                    "PYTHONPATH": str(ROOT_DIR.resolve()),
                },
            },
            "agent-control": {
                "command": sys.executable,
                "args": ["-m", "mcp_server.agent_control_mcp"],
                "env": {
                    **os.environ,
                    "PROJECT_NAME": self.project_name,
                    "PROJECT_DIR": str(self.project_dir.resolve()),
                    "API_BASE_URL": "http://localhost:8000",
                    "PYTHONPATH": str(ROOT_DIR.resolve()),
                },
            },
        }

        # Get system prompt with project context
        system_prompt = get_system_prompt(self.project_name, self.project_dir)

        # Use system Claude CLI
        system_cli = shutil.which("claude")

        try:
            self.client = ClaudeSDKClient(
                options=ClaudeAgentOptions(
                    model="claude-opus-4-5-20251101",
                    cli_path=system_cli,
                    system_prompt=system_prompt,
                    allowed_tools=[
                        *READONLY_BUILTIN_TOOLS,
                        *READONLY_FEATURE_MCP_TOOLS,
                        *AGENT_CONTROL_MCP_TOOLS,
                    ],
                    mcp_servers=mcp_servers,
                    permission_mode="bypassPermissions",
                    max_turns=100,
                    cwd=str(self.project_dir.resolve()),
                    settings=str(settings_file.resolve()),
                )
            )
            await self.client.__aenter__()
            self._client_entered = True
        except Exception as e:
            logger.exception("Failed to create Claude client")
            yield {"type": "error", "content": f"Failed to initialize assistant: {str(e)}"}
            return

        # Send initial greeting
        try:
            greeting = f"Hello! I'm your project assistant for **{self.project_name}**. I can help you understand the codebase, explain features, and answer questions about the project. What would you like to know?"

            # Store the greeting in the database
            add_message(self.project_dir, self.conversation_id, "assistant", greeting)

            yield {"type": "text", "content": greeting}
            yield {"type": "response_done"}
        except Exception as e:
            logger.exception("Failed to send greeting")
            yield {"type": "error", "content": f"Failed to start conversation: {str(e)}"}

    async def send_message(self, user_message: str) -> AsyncGenerator[dict, None]:
        """
        Send user message and stream Claude's response.

        Args:
            user_message: The user's message

        Yields:
            Message chunks:
            - {"type": "text", "content": str}
            - {"type": "tool_call", "tool": str, "input": dict}
            - {"type": "response_done"}
            - {"type": "error", "content": str}
        """
        if not self.client:
            yield {"type": "error", "content": "Session not initialized. Call start() first."}
            return

        if self.conversation_id is None:
            yield {"type": "error", "content": "No conversation ID set."}
            return

        # Store user message in database
        add_message(self.project_dir, self.conversation_id, "user", user_message)

        try:
            async for chunk in self._query_claude(user_message):
                yield chunk
            yield {"type": "response_done"}
        except Exception as e:
            logger.exception("Error during Claude query")
            yield {"type": "error", "content": f"Error: {str(e)}"}

    async def _query_claude(self, message: str) -> AsyncGenerator[dict, None]:
        """
        Internal method to query Claude and stream responses.

        Handles tool calls and text responses.
        """
        if not self.client:
            return

        # Send message to Claude
        await self.client.query(message)

        full_response = ""

        # Stream the response
        async for msg in self.client.receive_response():
            msg_type = type(msg).__name__

            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        text = block.text
                        if text:
                            full_response += text
                            yield {"type": "text", "content": text}

                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        tool_name = block.name
                        tool_input = getattr(block, "input", {})
                        yield {
                            "type": "tool_call",
                            "tool": tool_name,
                            "input": tool_input,
                        }

        # Store the complete response in the database
        if full_response and self.conversation_id:
            add_message(self.project_dir, self.conversation_id, "assistant", full_response)

    def get_conversation_id(self) -> Optional[int]:
        """Get the current conversation ID."""
        return self.conversation_id


# Session registry with thread safety
_sessions: dict[str, AssistantChatSession] = {}
_sessions_lock = threading.Lock()


def get_session(project_name: str) -> Optional[AssistantChatSession]:
    """Get an existing session for a project."""
    with _sessions_lock:
        return _sessions.get(project_name)


async def create_session(
    project_name: str,
    project_dir: Path,
    conversation_id: Optional[int] = None
) -> AssistantChatSession:
    """
    Create a new session for a project, closing any existing one.

    Args:
        project_name: Name of the project
        project_dir: Absolute path to the project directory
        conversation_id: Optional conversation ID to resume
    """
    old_session: Optional[AssistantChatSession] = None

    with _sessions_lock:
        old_session = _sessions.pop(project_name, None)
        session = AssistantChatSession(project_name, project_dir, conversation_id)
        _sessions[project_name] = session

    if old_session:
        try:
            await old_session.close()
        except Exception as e:
            logger.warning(f"Error closing old session for {project_name}: {e}")

    return session


async def remove_session(project_name: str) -> None:
    """Remove and close a session."""
    session: Optional[AssistantChatSession] = None

    with _sessions_lock:
        session = _sessions.pop(project_name, None)

    if session:
        try:
            await session.close()
        except Exception as e:
            logger.warning(f"Error closing session for {project_name}: {e}")


def list_sessions() -> list[str]:
    """List all active session project names."""
    with _sessions_lock:
        return list(_sessions.keys())


async def cleanup_all_sessions() -> None:
    """Close all active sessions. Called on server shutdown."""
    sessions_to_close: list[AssistantChatSession] = []

    with _sessions_lock:
        sessions_to_close = list(_sessions.values())
        _sessions.clear()

    for session in sessions_to_close:
        try:
            await session.close()
        except Exception as e:
            logger.warning(f"Error closing session {session.project_name}: {e}")
