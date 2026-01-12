"""
Multi-Agent Manager Service
===========================

Orchestrates multiple agent instances for a single project.
Handles agent spawning, feature assignment, and lifecycle management.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from .process_manager import AgentProcessManager, get_manager

# Import registry functions
import sys
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from registry import (
    create_project_agent,
    delete_project_agent,
    get_next_agent_id,
    get_or_create_default_config,
    get_project_agent,
    get_project_agents,
    get_project_config,
    update_project_agent,
    update_project_completion,
    update_project_last_run,
    update_project_status,
)

logger = logging.getLogger(__name__)

# Global registry of multi-agent managers
_multi_managers: dict[str, "MultiAgentManager"] = {}
_multi_managers_lock = asyncio.Lock()


class MultiAgentManager:
    """
    Manages multiple agent instances for a single project.

    Supports three modes:
    - separate: Each agent works on different features (default)
    - collaborative: Multiple agents work on the same feature
    - worktree: Each agent works in its own git worktree
    """

    def __init__(self, project_name: str, project_dir: Path):
        self.project_name = project_name
        self.project_dir = project_dir
        self.agents: dict[str, AgentProcessManager] = {}
        self.feature_locks: dict[int, str] = {}  # feature_id -> agent_id
        self._lock = asyncio.Lock()
        self._completion_check_task: Optional[asyncio.Task] = None
        self._output_callbacks: set[Callable[[str], None]] = set()

        # Load config
        self.config = get_or_create_default_config(project_name)

    @property
    def max_agents(self) -> int:
        """Maximum number of agents allowed."""
        return self.config.get("max_parallel_agents", 1)

    @property
    def use_worktrees(self) -> bool:
        """Whether to use git worktrees."""
        return self.config.get("use_worktrees", False)

    @property
    def auto_stop_on_completion(self) -> bool:
        """Whether to auto-stop agents when all features pass."""
        return self.config.get("auto_stop_on_completion", True)

    def reload_config(self) -> None:
        """Reload configuration from database."""
        self.config = get_or_create_default_config(self.project_name)

    async def spawn_agent(
        self,
        mode: str = "separate",
        worktree_path: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Spawn a new agent for this project.

        Args:
            mode: Agent mode (separate/collaborative/worktree)
            worktree_path: Optional path to git worktree

        Returns:
            Agent info dictionary

        Raises:
            ValueError: If max agents reached or invalid mode
        """
        async with self._lock:
            # Check limits
            current_count = len(self.agents)
            if current_count >= self.max_agents:
                raise ValueError(
                    f"Maximum agents ({self.max_agents}) reached for project {self.project_name}"
                )

            # Get next agent ID
            agent_id = get_next_agent_id(self.project_name)

            # Determine working directory
            if mode == "worktree" and worktree_path:
                work_dir = Path(worktree_path)
            else:
                work_dir = self.project_dir

            # Create agent entry in registry
            agent_info = create_project_agent(
                project_name=self.project_name,
                agent_id=agent_id,
                mode=mode,
                worktree_path=str(worktree_path) if worktree_path else None
            )

            # Create process manager for this agent
            manager = get_manager(
                project_name=f"{self.project_name}:{agent_id}",
                project_dir=work_dir,
                root_dir=ROOT_DIR
            )

            self.agents[agent_id] = manager

            logger.info(
                "Spawned agent %s for project %s (mode=%s)",
                agent_id, self.project_name, mode
            )

            return agent_info

    async def start_agent(
        self,
        agent_id: str,
        yolo_mode: bool = False,
        model: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Start a specific agent.

        Args:
            agent_id: The agent identifier
            yolo_mode: Whether to run in YOLO mode
            model: Model to use (optional)

        Returns:
            Agent status dictionary
        """
        async with self._lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")

            manager = self.agents[agent_id]

            # Register output callback
            async def output_callback(line: str):
                self._broadcast_output(agent_id, line)

            manager.add_output_callback(output_callback)

            # Start the agent
            success, message = await manager.start(yolo_mode=yolo_mode, model=model)

            if success:
                # Update registry
                update_project_agent(
                    self.project_name,
                    agent_id,
                    status="running",
                    pid=manager.pid,
                    started_at=datetime.now()
                )
                update_project_last_run(self.project_name)

                # Start completion check if not already running
                if self.auto_stop_on_completion and not self._completion_check_task:
                    self._completion_check_task = asyncio.create_task(
                        self._check_completion_loop()
                    )

            return {
                "success": success,
                "status": "running" if success else "stopped",
                "message": message,
                "pid": manager.pid if success else None
            }

    async def stop_agent(self, agent_id: str) -> dict[str, Any]:
        """Stop a specific agent."""
        async with self._lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")

            manager = self.agents[agent_id]
            result = await manager.stop()

            # Release any locked features
            self._release_features_for_agent(agent_id)

            # Update registry
            update_project_agent(
                self.project_name,
                agent_id,
                status="stopped",
                pid=None,
                current_feature_id=None
            )

            return result

    async def pause_agent(self, agent_id: str) -> dict[str, Any]:
        """Pause a specific agent."""
        async with self._lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")

            manager = self.agents[agent_id]
            result = await manager.pause()

            update_project_agent(self.project_name, agent_id, status="paused")

            return result

    async def resume_agent(self, agent_id: str) -> dict[str, Any]:
        """Resume a paused agent."""
        async with self._lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")

            manager = self.agents[agent_id]
            result = await manager.resume()

            update_project_agent(self.project_name, agent_id, status="running")

            return result

    async def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the project.

        Stops the agent if running and removes from registry.
        """
        async with self._lock:
            if agent_id in self.agents:
                manager = self.agents[agent_id]
                if manager.status in ("running", "paused"):
                    await manager.stop()

                self._release_features_for_agent(agent_id)
                del self.agents[agent_id]

            # Remove from registry
            return delete_project_agent(self.project_name, agent_id)

    async def stop_all(self) -> None:
        """Stop all agents for this project."""
        async with self._lock:
            for agent_id, manager in list(self.agents.items()):
                if manager.status in ("running", "paused"):
                    await manager.stop()
                    update_project_agent(
                        self.project_name,
                        agent_id,
                        status="stopped",
                        pid=None
                    )

            # Cancel completion check
            if self._completion_check_task:
                self._completion_check_task.cancel()
                self._completion_check_task = None

    def get_agent_status(self, agent_id: str) -> dict[str, Any]:
        """Get status of a specific agent."""
        if agent_id not in self.agents:
            # Try to get from registry
            agent_info = get_project_agent(self.project_name, agent_id)
            if agent_info:
                return agent_info
            raise ValueError(f"Agent {agent_id} not found")

        manager = self.agents[agent_id]
        return {
            "agent_id": agent_id,
            "status": manager.status,
            "pid": manager.pid,
            "started_at": manager.started_at.isoformat() if manager.started_at else None,
            "yolo_mode": manager.yolo_mode,
            "model": manager.model,
        }

    def get_all_agent_statuses(self) -> list[dict[str, Any]]:
        """Get status of all agents for this project."""
        statuses = []
        for agent_id in self.agents:
            statuses.append(self.get_agent_status(agent_id))
        return statuses

    def lock_feature(self, feature_id: int, agent_id: str) -> bool:
        """
        Lock a feature for a specific agent.

        Returns True if lock acquired, False if already locked by another agent.
        """
        if feature_id in self.feature_locks:
            if self.feature_locks[feature_id] != agent_id:
                return False
        self.feature_locks[feature_id] = agent_id
        return True

    def unlock_feature(self, feature_id: int, agent_id: str) -> bool:
        """
        Unlock a feature.

        Returns True if unlocked, False if not locked by this agent.
        """
        if feature_id in self.feature_locks:
            if self.feature_locks[feature_id] == agent_id:
                del self.feature_locks[feature_id]
                return True
        return False

    def get_locked_features(self) -> dict[int, str]:
        """Get all currently locked features."""
        return dict(self.feature_locks)

    def _release_features_for_agent(self, agent_id: str) -> None:
        """Release all features locked by an agent."""
        to_release = [
            fid for fid, aid in self.feature_locks.items()
            if aid == agent_id
        ]
        for fid in to_release:
            del self.feature_locks[fid]

    def _broadcast_output(self, agent_id: str, line: str) -> None:
        """Broadcast agent output to all registered callbacks."""
        prefixed_line = f"[{agent_id}] {line}"
        for callback in list(self._output_callbacks):
            try:
                callback(prefixed_line)
            except Exception as e:
                logger.error("Error in output callback: %s", e)

    def register_output_callback(self, callback: Callable[[str], None]) -> None:
        """Register a callback for agent output."""
        self._output_callbacks.add(callback)

    def unregister_output_callback(self, callback: Callable[[str], None]) -> None:
        """Unregister an output callback."""
        self._output_callbacks.discard(callback)

    async def _check_completion_loop(self) -> None:
        """Periodically check if all features are complete."""
        from api.database import create_database, Feature

        check_interval = 30  # seconds

        while True:
            try:
                await asyncio.sleep(check_interval)

                # Check if any agents are still running
                running_agents = [
                    aid for aid, mgr in self.agents.items()
                    if mgr.status == "running"
                ]

                if not running_agents:
                    continue

                # Check completion status
                _, SessionLocal = create_database(self.project_dir)
                session = SessionLocal()
                try:
                    total = session.query(Feature).count()
                    passing = session.query(Feature).filter(Feature.passes == True).count()

                    if total > 0:
                        percentage = (passing / total) * 100
                        update_project_completion(self.project_name, percentage)

                        if passing == total:
                            logger.info(
                                "All features passing for %s, stopping agents",
                                self.project_name
                            )
                            await self.stop_all()
                            update_project_status(self.project_name, "finished")
                            break
                finally:
                    session.close()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in completion check: %s", e)


async def get_multi_manager(project_name: str, project_dir: Path) -> MultiAgentManager:
    """
    Get or create a MultiAgentManager for a project.

    This is the main entry point for getting a multi-agent manager instance.
    """
    async with _multi_managers_lock:
        if project_name not in _multi_managers:
            manager = MultiAgentManager(project_name, project_dir)

            # Load existing agents from registry
            existing_agents = get_project_agents(project_name)
            for agent_info in existing_agents:
                agent_id = agent_info["agent_id"]
                work_dir = Path(agent_info["worktree_path"]) if agent_info.get("worktree_path") else project_dir

                proc_manager = get_manager(
                    project_name=f"{project_name}:{agent_id}",
                    project_dir=work_dir,
                    root_dir=ROOT_DIR
                )
                manager.agents[agent_id] = proc_manager

            _multi_managers[project_name] = manager

        return _multi_managers[project_name]


async def remove_multi_manager(project_name: str) -> None:
    """Remove a multi-agent manager (cleanup on project deletion)."""
    async with _multi_managers_lock:
        if project_name in _multi_managers:
            manager = _multi_managers[project_name]
            await manager.stop_all()
            del _multi_managers[project_name]
