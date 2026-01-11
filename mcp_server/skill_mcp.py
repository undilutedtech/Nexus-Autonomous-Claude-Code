#!/usr/bin/env python3
"""
MCP Server for Local Skill Invocation
======================================

Provides tools to discover and invoke skills from the local workstation.
Skills are loaded from:
1. Nexus root: {nexus_root}/.claude/skills/
2. Project-specific: {project_dir}/.claude/skills/

Also supports commands from .claude/commands/ directories.

Tools:
- skill_list: List all available skills
- skill_get: Get full content of a skill
- skill_invoke: Invoke a skill (returns content + marks as active)
- command_list: List all available commands
- command_get: Get full content of a command
"""

import json
import os
import re
from pathlib import Path
from typing import Annotated

import yaml
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Configuration from environment
PROJECT_DIR = Path(os.environ.get("PROJECT_DIR", ".")).resolve()
NEXUS_ROOT = Path(os.environ.get("NEXUS_ROOT", Path(__file__).parent.parent)).resolve()

# Initialize the MCP server
mcp = FastMCP("skills")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from markdown content.

    Returns:
        (metadata_dict, remaining_content)
    """
    if not content.startswith("---"):
        return {}, content

    # Find the closing ---
    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return {}, content

    frontmatter_end = end_match.start() + 3
    frontmatter_str = content[3:frontmatter_end]
    remaining = content[frontmatter_end + end_match.end() - end_match.start():]

    try:
        metadata = yaml.safe_load(frontmatter_str) or {}
    except yaml.YAMLError:
        metadata = {}

    return metadata, remaining.strip()


def discover_skills() -> list[dict]:
    """
    Discover all available skills from both nexus root and project directory.

    Returns:
        List of skill metadata dicts with keys:
        - name: Skill name (directory name)
        - description: From SKILL.md frontmatter
        - source: "nexus" or "project"
        - path: Full path to SKILL.md
    """
    skills = []

    # Search locations in priority order (project overrides nexus)
    search_paths = [
        (NEXUS_ROOT / ".claude" / "skills", "nexus"),
        (PROJECT_DIR / ".claude" / "skills", "project"),
    ]

    seen_names = set()

    for base_path, source in search_paths:
        if not base_path.exists():
            continue

        for skill_dir in base_path.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            skill_name = skill_dir.name

            # Project skills override nexus skills
            if skill_name in seen_names and source == "nexus":
                continue

            try:
                content = skill_file.read_text(encoding="utf-8")
                metadata, _ = parse_frontmatter(content)

                skill_info = {
                    "name": skill_name,
                    "description": metadata.get("description", f"Skill: {skill_name}"),
                    "source": source,
                    "path": str(skill_file),
                }

                # Add any additional metadata
                if "license" in metadata:
                    skill_info["license"] = metadata["license"]
                if "version" in metadata:
                    skill_info["version"] = metadata["version"]
                if "author" in metadata:
                    skill_info["author"] = metadata["author"]

                skills.append(skill_info)
                seen_names.add(skill_name)

            except Exception as e:
                # Skip skills that can't be read
                continue

    return skills


def discover_commands() -> list[dict]:
    """
    Discover all available commands from both nexus root and project directory.

    Returns:
        List of command metadata dicts with keys:
        - name: Command name (file name without .md)
        - description: From command frontmatter
        - source: "nexus" or "project"
        - path: Full path to command file
    """
    commands = []

    # Search locations in priority order (project overrides nexus)
    search_paths = [
        (NEXUS_ROOT / ".claude" / "commands", "nexus"),
        (PROJECT_DIR / ".claude" / "commands", "project"),
    ]

    seen_names = set()

    for base_path, source in search_paths:
        if not base_path.exists():
            continue

        for cmd_file in base_path.glob("*.md"):
            cmd_name = cmd_file.stem

            # Project commands override nexus commands
            if cmd_name in seen_names and source == "nexus":
                continue

            try:
                content = cmd_file.read_text(encoding="utf-8")
                metadata, _ = parse_frontmatter(content)

                command_info = {
                    "name": cmd_name,
                    "description": metadata.get("description", f"Command: {cmd_name}"),
                    "source": source,
                    "path": str(cmd_file),
                }

                commands.append(command_info)
                seen_names.add(cmd_name)

            except Exception:
                continue

    return commands


def get_skill_content(skill_name: str) -> tuple[dict | None, str | None, str | None]:
    """
    Get the full content of a skill.

    Returns:
        (metadata, content, error) - error is set if skill not found
    """
    # Search in project first, then nexus root
    search_paths = [
        PROJECT_DIR / ".claude" / "skills" / skill_name / "SKILL.md",
        NEXUS_ROOT / ".claude" / "skills" / skill_name / "SKILL.md",
    ]

    for skill_path in search_paths:
        if skill_path.exists():
            try:
                full_content = skill_path.read_text(encoding="utf-8")
                metadata, content = parse_frontmatter(full_content)
                return metadata, content, None
            except Exception as e:
                return None, None, f"Error reading skill: {e}"

    return None, None, f"Skill '{skill_name}' not found"


def get_command_content(command_name: str) -> tuple[dict | None, str | None, str | None]:
    """
    Get the full content of a command.

    Returns:
        (metadata, content, error) - error is set if command not found
    """
    # Search in project first, then nexus root
    search_paths = [
        PROJECT_DIR / ".claude" / "commands" / f"{command_name}.md",
        NEXUS_ROOT / ".claude" / "commands" / f"{command_name}.md",
    ]

    for cmd_path in search_paths:
        if cmd_path.exists():
            try:
                full_content = cmd_path.read_text(encoding="utf-8")
                metadata, content = parse_frontmatter(full_content)
                return metadata, content, None
            except Exception as e:
                return None, None, f"Error reading command: {e}"

    return None, None, f"Command '{command_name}' not found"


@mcp.tool()
def skill_list() -> str:
    """List all available skills from the local workstation.

    Discovers skills from:
    1. Project directory: {project}/.claude/skills/
    2. Nexus root: {nexus}/.claude/skills/

    Project skills override nexus skills with the same name.

    Returns:
        JSON with: skills (list of skill info objects)
    """
    skills = discover_skills()

    return json.dumps({
        "skills": skills,
        "count": len(skills),
        "sources": {
            "project": str(PROJECT_DIR / ".claude" / "skills"),
            "nexus": str(NEXUS_ROOT / ".claude" / "skills"),
        }
    }, indent=2)


@mcp.tool()
def skill_get(
    skill_name: Annotated[str, Field(description="Name of the skill to retrieve")]
) -> str:
    """Get the full content of a skill.

    Returns the skill's metadata (from YAML frontmatter) and full content.
    Use this to understand what a skill provides before invoking it.

    Args:
        skill_name: Name of the skill (e.g., "frontend-design")

    Returns:
        JSON with: name, metadata, content, or error if not found
    """
    metadata, content, error = get_skill_content(skill_name)

    if error:
        return json.dumps({"error": error})

    return json.dumps({
        "name": skill_name,
        "metadata": metadata,
        "content": content,
    }, indent=2)


@mcp.tool()
def skill_invoke(
    skill_name: Annotated[str, Field(description="Name of the skill to invoke")],
    context: Annotated[str | None, Field(description="Optional context or arguments for the skill")] = None
) -> str:
    """Invoke a skill and get its guidelines.

    Use this when you want to apply a skill to your current task.
    The skill content provides detailed guidelines that you should follow.

    For example, invoking "frontend-design" will return design guidelines
    that you should apply when creating UI components.

    Args:
        skill_name: Name of the skill to invoke (e.g., "frontend-design")
        context: Optional context about what you're working on

    Returns:
        JSON with skill content and instructions, or error if not found
    """
    metadata, content, error = get_skill_content(skill_name)

    if error:
        return json.dumps({"error": error})

    result = {
        "skill": skill_name,
        "description": metadata.get("description", ""),
        "status": "active",
        "instructions": content,
    }

    if context:
        result["context"] = context
        result["guidance"] = (
            f"Apply the '{skill_name}' skill guidelines to the following context:\n\n"
            f"{context}\n\n"
            f"Follow the skill instructions below to complete this task with high quality."
        )

    return json.dumps(result, indent=2)


@mcp.tool()
def command_list() -> str:
    """List all available commands from the local workstation.

    Discovers commands from:
    1. Project directory: {project}/.claude/commands/
    2. Nexus root: {nexus}/.claude/commands/

    Project commands override nexus commands with the same name.

    Returns:
        JSON with: commands (list of command info objects)
    """
    commands = discover_commands()

    return json.dumps({
        "commands": commands,
        "count": len(commands),
        "sources": {
            "project": str(PROJECT_DIR / ".claude" / "commands"),
            "nexus": str(NEXUS_ROOT / ".claude" / "commands"),
        }
    }, indent=2)


@mcp.tool()
def command_get(
    command_name: Annotated[str, Field(description="Name of the command to retrieve")]
) -> str:
    """Get the full content of a command.

    Returns the command's metadata and instructions.
    Commands provide step-by-step workflows for complex tasks.

    Args:
        command_name: Name of the command (e.g., "checkpoint", "create-spec")

    Returns:
        JSON with: name, metadata, content, or error if not found
    """
    metadata, content, error = get_command_content(command_name)

    if error:
        return json.dumps({"error": error})

    return json.dumps({
        "name": command_name,
        "metadata": metadata,
        "content": content,
    }, indent=2)


@mcp.tool()
def command_invoke(
    command_name: Annotated[str, Field(description="Name of the command to invoke")],
    args: Annotated[str | None, Field(description="Optional arguments for the command")] = None
) -> str:
    """Invoke a command and get its instructions.

    Use this to execute a predefined workflow. The command content provides
    step-by-step instructions that you should follow.

    Args:
        command_name: Name of the command (e.g., "checkpoint")
        args: Optional arguments for the command

    Returns:
        JSON with command instructions, or error if not found
    """
    metadata, content, error = get_command_content(command_name)

    if error:
        return json.dumps({"error": error})

    result = {
        "command": command_name,
        "description": metadata.get("description", ""),
        "status": "active",
        "instructions": content,
    }

    if args:
        result["args"] = args
        result["guidance"] = (
            f"Execute the '{command_name}' command with the following arguments:\n\n"
            f"{args}\n\n"
            f"Follow the command instructions below."
        )

    return json.dumps(result, indent=2)


@mcp.tool()
def skill_create(
    skill_name: Annotated[str, Field(description="Name for the new skill")],
    description: Annotated[str, Field(description="Brief description of what the skill does")],
    content: Annotated[str, Field(description="Full skill content/guidelines in markdown")]
) -> str:
    """Create a new project-specific skill.

    Creates a skill in the project's .claude/skills/ directory.
    This skill will be available for future invocations.

    Args:
        skill_name: Name for the skill (will be the directory name)
        description: Brief description for the skill
        content: Full markdown content with guidelines

    Returns:
        JSON with: success, path, or error
    """
    # Validate skill name
    if not re.match(r'^[a-zA-Z0-9_-]+$', skill_name):
        return json.dumps({
            "error": "Invalid skill name. Use only letters, numbers, hyphens, and underscores."
        })

    skill_dir = PROJECT_DIR / ".claude" / "skills" / skill_name
    skill_file = skill_dir / "SKILL.md"

    try:
        # Create directory
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Build skill content with frontmatter
        frontmatter = {
            "name": skill_name,
            "description": description,
        }

        full_content = f"""---
{yaml.dump(frontmatter, default_flow_style=False).strip()}
---

{content}
"""

        skill_file.write_text(full_content, encoding="utf-8")

        return json.dumps({
            "success": True,
            "message": f"Skill '{skill_name}' created successfully",
            "path": str(skill_file),
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to create skill: {e}"})


if __name__ == "__main__":
    mcp.run()
