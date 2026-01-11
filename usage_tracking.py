"""
Usage Tracking Module
=====================

Tracks token usage and costs across agent sessions.
Provides cost limits and usage statistics.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration via environment variables
MAX_COST_USD = float(os.environ.get("NEXUS_MAX_COST_USD", "0"))  # 0 = no limit
MAX_TOKENS = int(os.environ.get("NEXUS_MAX_TOKENS", "0"))  # 0 = no limit

# Model pricing (per 1M tokens) - Updated January 2025
# https://www.anthropic.com/pricing
MODEL_PRICING = {
    # Claude Opus 4.5
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
    "claude-opus-4-5": {"input": 15.00, "output": 75.00},
    # Claude Sonnet 4.5
    "claude-sonnet-4-5-20250514": {"input": 3.00, "output": 15.00},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
    # Claude Sonnet 4
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    # Claude 3.5 Sonnet (legacy)
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    # Claude 3.5 Haiku
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
    "claude-3-5-haiku": {"input": 0.80, "output": 4.00},
    # Default fallback
    "default": {"input": 3.00, "output": 15.00},
}

USAGE_FILE = ".usage_stats.json"


@dataclass
class SessionUsage:
    """Usage data for a single session."""

    session_id: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    duration_api_ms: int = 0
    num_turns: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_creation_tokens": self.cache_creation_tokens,
            "cost_usd": self.cost_usd,
            "duration_ms": self.duration_ms,
            "duration_api_ms": self.duration_api_ms,
            "num_turns": self.num_turns,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionUsage":
        return cls(
            session_id=data.get("session_id", "unknown"),
            model=data.get("model", "unknown"),
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            cache_read_tokens=data.get("cache_read_tokens", 0),
            cache_creation_tokens=data.get("cache_creation_tokens", 0),
            cost_usd=data.get("cost_usd", 0.0),
            duration_ms=data.get("duration_ms", 0),
            duration_api_ms=data.get("duration_api_ms", 0),
            num_turns=data.get("num_turns", 0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


@dataclass
class UsageStats:
    """Aggregate usage statistics."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_read_tokens: int = 0
    total_cache_creation_tokens: int = 0
    total_cost_usd: float = 0.0
    total_duration_ms: int = 0
    total_sessions: int = 0
    sessions: list[SessionUsage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cache_read_tokens": self.total_cache_read_tokens,
            "total_cache_creation_tokens": self.total_cache_creation_tokens,
            "total_cost_usd": self.total_cost_usd,
            "total_duration_ms": self.total_duration_ms,
            "total_sessions": self.total_sessions,
            "sessions": [s.to_dict() for s in self.sessions],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UsageStats":
        sessions = [SessionUsage.from_dict(s) for s in data.get("sessions", [])]
        return cls(
            total_input_tokens=data.get("total_input_tokens", 0),
            total_output_tokens=data.get("total_output_tokens", 0),
            total_cache_read_tokens=data.get("total_cache_read_tokens", 0),
            total_cache_creation_tokens=data.get("total_cache_creation_tokens", 0),
            total_cost_usd=data.get("total_cost_usd", 0.0),
            total_duration_ms=data.get("total_duration_ms", 0),
            total_sessions=data.get("total_sessions", 0),
            sessions=sessions,
        )

    def add_session(self, session: SessionUsage) -> None:
        """Add a session's usage to the totals."""
        self.total_input_tokens += session.input_tokens
        self.total_output_tokens += session.output_tokens
        self.total_cache_read_tokens += session.cache_read_tokens
        self.total_cache_creation_tokens += session.cache_creation_tokens
        self.total_cost_usd += session.cost_usd
        self.total_duration_ms += session.duration_ms
        self.total_sessions += 1
        self.sessions.append(session)

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.total_input_tokens + self.total_output_tokens


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
) -> float:
    """
    Calculate the cost for a session based on token usage.

    Args:
        model: Model name/ID
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cache_read_tokens: Number of cache read tokens (90% discount)
        cache_creation_tokens: Number of cache creation tokens (25% premium)

    Returns:
        Estimated cost in USD
    """
    # Get pricing for the model
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])

    # Calculate base costs (per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    # Cache read tokens get 90% discount on input price
    cache_read_cost = (cache_read_tokens / 1_000_000) * pricing["input"] * 0.1

    # Cache creation tokens get 25% premium on input price
    cache_creation_cost = (cache_creation_tokens / 1_000_000) * pricing["input"] * 1.25

    return input_cost + output_cost + cache_read_cost + cache_creation_cost


def load_usage_stats(project_dir: Path) -> UsageStats:
    """Load usage statistics from file."""
    usage_file = project_dir / USAGE_FILE

    if not usage_file.exists():
        return UsageStats()

    try:
        data = json.loads(usage_file.read_text(encoding="utf-8"))
        return UsageStats.from_dict(data)
    except Exception:
        return UsageStats()


def save_usage_stats(project_dir: Path, stats: UsageStats) -> None:
    """Save usage statistics to file."""
    usage_file = project_dir / USAGE_FILE

    try:
        usage_file.write_text(
            json.dumps(stats.to_dict(), indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"Warning: Failed to save usage stats: {e}")


def record_session_usage(
    project_dir: Path,
    session_id: str,
    model: str,
    usage: dict[str, Any] | None,
    total_cost_usd: float | None,
    duration_ms: int,
    duration_api_ms: int,
    num_turns: int,
) -> SessionUsage:
    """
    Record usage from a completed session.

    Args:
        project_dir: Project directory
        session_id: Session identifier
        model: Model used
        usage: Usage dictionary from ResultMessage
        total_cost_usd: Cost from ResultMessage (if available)
        duration_ms: Total duration in milliseconds
        duration_api_ms: API duration in milliseconds
        num_turns: Number of conversation turns

    Returns:
        SessionUsage object with recorded data
    """
    # Extract token counts from usage dict
    input_tokens = 0
    output_tokens = 0
    cache_read_tokens = 0
    cache_creation_tokens = 0

    if usage:
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cache_read_tokens = usage.get("cache_read_tokens", 0) or usage.get(
            "cache_read_input_tokens", 0
        )
        cache_creation_tokens = usage.get("cache_creation_tokens", 0) or usage.get(
            "cache_creation_input_tokens", 0
        )

    # Use provided cost or calculate it
    if total_cost_usd is not None:
        cost = total_cost_usd
    else:
        cost = calculate_cost(
            model, input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens
        )

    # Create session usage record
    session = SessionUsage(
        session_id=session_id,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read_tokens,
        cache_creation_tokens=cache_creation_tokens,
        cost_usd=cost,
        duration_ms=duration_ms,
        duration_api_ms=duration_api_ms,
        num_turns=num_turns,
    )

    # Load existing stats, add session, and save
    stats = load_usage_stats(project_dir)
    stats.add_session(session)
    save_usage_stats(project_dir, stats)

    return session


def check_cost_limit(project_dir: Path) -> tuple[bool, str]:
    """
    Check if the cost limit has been exceeded.

    Returns:
        (exceeded, reason) tuple where:
        - exceeded: True if limit exceeded
        - reason: Human-readable explanation
    """
    if MAX_COST_USD <= 0:
        return False, ""

    stats = load_usage_stats(project_dir)

    if stats.total_cost_usd >= MAX_COST_USD:
        return True, (
            f"Cost limit exceeded: ${stats.total_cost_usd:.4f} >= ${MAX_COST_USD:.2f}\n"
            f"Total tokens used: {stats.total_tokens:,}\n"
            f"Sessions: {stats.total_sessions}"
        )

    return False, ""


def check_token_limit(project_dir: Path) -> tuple[bool, str]:
    """
    Check if the token limit has been exceeded.

    Returns:
        (exceeded, reason) tuple where:
        - exceeded: True if limit exceeded
        - reason: Human-readable explanation
    """
    if MAX_TOKENS <= 0:
        return False, ""

    stats = load_usage_stats(project_dir)

    if stats.total_tokens >= MAX_TOKENS:
        return True, (
            f"Token limit exceeded: {stats.total_tokens:,} >= {MAX_TOKENS:,}\n"
            f"Total cost: ${stats.total_cost_usd:.4f}\n"
            f"Sessions: {stats.total_sessions}"
        )

    return False, ""


def check_usage_limits(project_dir: Path) -> tuple[bool, str]:
    """
    Check if any usage limit has been exceeded.

    Returns:
        (exceeded, reason) tuple
    """
    # Check cost limit
    exceeded, reason = check_cost_limit(project_dir)
    if exceeded:
        return exceeded, reason

    # Check token limit
    exceeded, reason = check_token_limit(project_dir)
    if exceeded:
        return exceeded, reason

    return False, ""


def get_usage_summary(project_dir: Path) -> str:
    """Get a formatted summary of usage statistics."""
    stats = load_usage_stats(project_dir)

    if stats.total_sessions == 0:
        return "No usage data recorded yet."

    # Calculate averages
    avg_tokens = stats.total_tokens / stats.total_sessions
    avg_cost = stats.total_cost_usd / stats.total_sessions
    avg_duration = stats.total_duration_ms / stats.total_sessions / 1000  # seconds

    lines = [
        f"Sessions: {stats.total_sessions}",
        f"Total tokens: {stats.total_tokens:,} (in: {stats.total_input_tokens:,}, out: {stats.total_output_tokens:,})",
        f"Total cost: ${stats.total_cost_usd:.4f}",
        f"Total time: {stats.total_duration_ms / 1000:.1f}s",
        f"Averages per session: {avg_tokens:,.0f} tokens, ${avg_cost:.4f}, {avg_duration:.1f}s",
    ]

    # Add limit info if configured
    if MAX_COST_USD > 0:
        remaining = MAX_COST_USD - stats.total_cost_usd
        lines.append(f"Cost limit: ${MAX_COST_USD:.2f} (${remaining:.4f} remaining)")

    if MAX_TOKENS > 0:
        remaining = MAX_TOKENS - stats.total_tokens
        lines.append(f"Token limit: {MAX_TOKENS:,} ({remaining:,} remaining)")

    return "\n".join(lines)


def print_session_usage(session: SessionUsage) -> None:
    """Print usage information for a session."""
    total_tokens = session.input_tokens + session.output_tokens

    print(f"\n{'─' * 50}")
    print("Session Usage:")
    print(f"  Tokens: {total_tokens:,} (in: {session.input_tokens:,}, out: {session.output_tokens:,})")

    if session.cache_read_tokens > 0 or session.cache_creation_tokens > 0:
        print(f"  Cache: read {session.cache_read_tokens:,}, created {session.cache_creation_tokens:,}")

    print(f"  Cost: ${session.cost_usd:.4f}")
    print(f"  Duration: {session.duration_ms / 1000:.1f}s (API: {session.duration_api_ms / 1000:.1f}s)")
    print(f"  Turns: {session.num_turns}")
    print(f"{'─' * 50}")


def print_usage_summary(project_dir: Path) -> None:
    """Print a summary of total usage."""
    print(f"\n{'═' * 50}")
    print("Usage Summary:")
    print(get_usage_summary(project_dir))
    print(f"{'═' * 50}")


def reset_usage_stats(project_dir: Path) -> None:
    """Reset all usage statistics."""
    usage_file = project_dir / USAGE_FILE

    if usage_file.exists():
        usage_file.unlink()


def get_remaining_budget(project_dir: Path) -> tuple[float | None, int | None]:
    """
    Get remaining budget before limits are hit.

    Returns:
        (remaining_cost, remaining_tokens) - None if no limit set
    """
    stats = load_usage_stats(project_dir)

    remaining_cost = None
    if MAX_COST_USD > 0:
        remaining_cost = max(0, MAX_COST_USD - stats.total_cost_usd)

    remaining_tokens = None
    if MAX_TOKENS > 0:
        remaining_tokens = max(0, MAX_TOKENS - stats.total_tokens)

    return remaining_cost, remaining_tokens
