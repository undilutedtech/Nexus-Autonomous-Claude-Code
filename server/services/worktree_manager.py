"""
Git Worktree Manager Service
============================

Manages git worktrees for parallel agent isolation.
Provides worktree creation, cleanup, and synchronization.
"""

import asyncio
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WorktreeManager:
    """
    Manages git worktrees for a project.

    Git worktrees allow multiple working directories from the same repository,
    enabling parallel agent work on different branches/features without conflicts.
    """

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir.resolve()
        self.worktrees_base = self.project_dir.parent  # Worktrees go alongside project

    def _run_git(self, *args, cwd: Optional[Path] = None) -> tuple[bool, str]:
        """
        Run a git command.

        Returns:
            Tuple of (success, output)
        """
        cmd = ["git"] + list(args)
        work_dir = cwd or self.project_dir

        try:
            result = subprocess.run(
                cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def is_git_repo(self) -> bool:
        """Check if the project directory is a git repository."""
        git_dir = self.project_dir / ".git"
        return git_dir.exists()

    async def init_repository(self) -> bool:
        """
        Initialize a git repository if not already initialized.

        Returns:
            True if repo exists or was created, False on error
        """
        if self.is_git_repo():
            return True

        loop = asyncio.get_event_loop()
        success, output = await loop.run_in_executor(
            None, lambda: self._run_git("init")
        )

        if success:
            logger.info("Initialized git repository at %s", self.project_dir)

            # Create initial commit
            await loop.run_in_executor(
                None, lambda: self._run_git("add", "-A")
            )
            await loop.run_in_executor(
                None, lambda: self._run_git("commit", "-m", "Initial commit")
            )

        return success

    async def create_worktree(
        self,
        agent_id: str,
        branch: Optional[str] = None
    ) -> Optional[Path]:
        """
        Create a git worktree for an agent.

        Args:
            agent_id: Unique agent identifier
            branch: Branch name (defaults to agent_id based branch)

        Returns:
            Path to the worktree, or None on failure
        """
        # Ensure git repo exists
        if not await self.init_repository():
            logger.error("Failed to initialize git repository")
            return None

        # Worktree path: {project_parent}/{project_name}-{agent_id}
        project_name = self.project_dir.name
        worktree_name = f"{project_name}-{agent_id}"
        worktree_path = self.worktrees_base / worktree_name

        # Branch name
        if not branch:
            branch = f"agent/{agent_id}"

        loop = asyncio.get_event_loop()

        # Create the worktree with a new branch
        success, output = await loop.run_in_executor(
            None,
            lambda: self._run_git(
                "worktree", "add", "-b", branch,
                str(worktree_path)
            )
        )

        if not success:
            # Try without creating a new branch (branch might exist)
            success, output = await loop.run_in_executor(
                None,
                lambda: self._run_git(
                    "worktree", "add",
                    str(worktree_path), branch
                )
            )

        if success:
            logger.info("Created worktree at %s (branch: %s)", worktree_path, branch)
            return worktree_path
        else:
            logger.error("Failed to create worktree: %s", output)
            return None

    async def cleanup_worktree(self, agent_id: str) -> bool:
        """
        Remove a worktree for an agent.

        Args:
            agent_id: The agent identifier

        Returns:
            True if removed successfully
        """
        project_name = self.project_dir.name
        worktree_name = f"{project_name}-{agent_id}"
        worktree_path = self.worktrees_base / worktree_name

        if not worktree_path.exists():
            return True

        loop = asyncio.get_event_loop()

        # Remove the worktree
        success, output = await loop.run_in_executor(
            None,
            lambda: self._run_git("worktree", "remove", str(worktree_path), "--force")
        )

        if success:
            logger.info("Removed worktree at %s", worktree_path)

            # Also delete the branch if it exists
            branch = f"agent/{agent_id}"
            await loop.run_in_executor(
                None,
                lambda: self._run_git("branch", "-D", branch)
            )

            return True
        else:
            # Try force removal via filesystem
            try:
                shutil.rmtree(worktree_path)

                # Prune worktrees
                await loop.run_in_executor(
                    None,
                    lambda: self._run_git("worktree", "prune")
                )

                logger.info("Force removed worktree at %s", worktree_path)
                return True
            except Exception as e:
                logger.error("Failed to remove worktree: %s", e)
                return False

    async def merge_worktree(
        self,
        agent_id: str,
        target_branch: str = "main"
    ) -> tuple[bool, str]:
        """
        Merge changes from a worktree branch into the target branch.

        Args:
            agent_id: The agent identifier
            target_branch: Branch to merge into (default: main)

        Returns:
            Tuple of (success, message)
        """
        source_branch = f"agent/{agent_id}"

        loop = asyncio.get_event_loop()

        # Switch to target branch
        success, output = await loop.run_in_executor(
            None,
            lambda: self._run_git("checkout", target_branch)
        )

        if not success:
            return False, f"Failed to checkout {target_branch}: {output}"

        # Merge the agent branch
        success, output = await loop.run_in_executor(
            None,
            lambda: self._run_git("merge", source_branch, "--no-ff", "-m",
                                  f"Merge {source_branch} into {target_branch}")
        )

        if success:
            logger.info("Merged %s into %s", source_branch, target_branch)
            return True, f"Successfully merged {source_branch} into {target_branch}"
        else:
            # Abort merge on conflict
            await loop.run_in_executor(
                None,
                lambda: self._run_git("merge", "--abort")
            )
            return False, f"Merge conflict: {output}"

    async def list_worktrees(self) -> list[dict[str, Any]]:
        """
        List all worktrees for this project.

        Returns:
            List of worktree info dictionaries
        """
        if not self.is_git_repo():
            return []

        loop = asyncio.get_event_loop()
        success, output = await loop.run_in_executor(
            None,
            lambda: self._run_git("worktree", "list", "--porcelain")
        )

        if not success:
            return []

        worktrees = []
        current_worktree = {}

        for line in output.split("\n"):
            line = line.strip()
            if not line:
                if current_worktree:
                    worktrees.append(current_worktree)
                    current_worktree = {}
                continue

            if line.startswith("worktree "):
                current_worktree["path"] = line[9:]
            elif line.startswith("HEAD "):
                current_worktree["head"] = line[5:]
            elif line.startswith("branch "):
                current_worktree["branch"] = line[7:]
            elif line == "bare":
                current_worktree["bare"] = True
            elif line == "detached":
                current_worktree["detached"] = True

        if current_worktree:
            worktrees.append(current_worktree)

        # Filter to only include agent worktrees
        project_name = self.project_dir.name
        agent_worktrees = []
        for wt in worktrees:
            path = Path(wt.get("path", ""))
            if path.name.startswith(f"{project_name}-agent-"):
                # Extract agent ID from path
                agent_id = path.name.replace(f"{project_name}-", "")
                wt["agent_id"] = agent_id
                agent_worktrees.append(wt)

        return agent_worktrees

    async def sync_worktrees(self, target_branch: str = "main") -> list[dict[str, Any]]:
        """
        Sync all worktrees with the latest changes from target branch.

        Returns:
            List of sync results
        """
        worktrees = await self.list_worktrees()
        results = []

        loop = asyncio.get_event_loop()

        for wt in worktrees:
            wt_path = Path(wt["path"])
            agent_id = wt.get("agent_id", "unknown")

            # Fetch latest
            await loop.run_in_executor(
                None,
                lambda p=wt_path: self._run_git("fetch", "origin", cwd=p)
            )

            # Rebase on target branch
            success, output = await loop.run_in_executor(
                None,
                lambda p=wt_path: self._run_git("rebase", f"origin/{target_branch}", cwd=p)
            )

            if success:
                results.append({
                    "agent_id": agent_id,
                    "path": str(wt_path),
                    "success": True,
                    "message": "Synced successfully"
                })
            else:
                # Abort rebase on conflict
                await loop.run_in_executor(
                    None,
                    lambda p=wt_path: self._run_git("rebase", "--abort", cwd=p)
                )
                results.append({
                    "agent_id": agent_id,
                    "path": str(wt_path),
                    "success": False,
                    "message": f"Sync failed: {output}"
                })

        return results

    async def get_worktree_status(self, agent_id: str) -> Optional[dict[str, Any]]:
        """
        Get status of a specific worktree.

        Returns:
            Worktree status dictionary, or None if not found
        """
        project_name = self.project_dir.name
        worktree_name = f"{project_name}-{agent_id}"
        worktree_path = self.worktrees_base / worktree_name

        if not worktree_path.exists():
            return None

        loop = asyncio.get_event_loop()

        # Get current branch
        _, branch = await loop.run_in_executor(
            None,
            lambda: self._run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=worktree_path)
        )

        # Get status
        _, status = await loop.run_in_executor(
            None,
            lambda: self._run_git("status", "--porcelain", cwd=worktree_path)
        )

        # Get last commit
        _, last_commit = await loop.run_in_executor(
            None,
            lambda: self._run_git("log", "-1", "--format=%H %s", cwd=worktree_path)
        )

        return {
            "agent_id": agent_id,
            "path": str(worktree_path),
            "branch": branch,
            "has_changes": bool(status),
            "changes": status.split("\n") if status else [],
            "last_commit": last_commit,
        }


# Cache of worktree managers per project
_worktree_managers: dict[str, WorktreeManager] = {}


def get_worktree_manager(project_dir: Path) -> WorktreeManager:
    """Get or create a WorktreeManager for a project."""
    key = str(project_dir.resolve())
    if key not in _worktree_managers:
        _worktree_managers[key] = WorktreeManager(project_dir)
    return _worktree_managers[key]
