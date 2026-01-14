"""
Prompt Loading Utilities
========================

Functions for loading prompt templates with project-specific support.

Fallback chain:
1. Project-specific: {project_dir}/prompts/{name}.md
2. Base template: .claude/templates/{name}.template.md
"""

import shutil
from pathlib import Path

# Base templates location (generic templates)
TEMPLATES_DIR = Path(__file__).parent / ".claude" / "templates"


def get_project_prompts_dir(project_dir: Path) -> Path:
    """Get the prompts directory for a specific project."""
    return project_dir / "prompts"


def load_prompt(name: str, project_dir: Path | None = None) -> str:
    """
    Load a prompt template with fallback chain.

    Fallback order:
    1. Project-specific: {project_dir}/prompts/{name}.md
    2. Base template: .claude/templates/{name}.template.md

    Args:
        name: The prompt name (without extension), e.g., "initializer_prompt"
        project_dir: Optional project directory for project-specific prompts

    Returns:
        The prompt content as a string

    Raises:
        FileNotFoundError: If prompt not found in any location
    """
    # 1. Try project-specific first
    if project_dir:
        project_prompts = get_project_prompts_dir(project_dir)
        project_path = project_prompts / f"{name}.md"
        if project_path.exists():
            try:
                return project_path.read_text(encoding="utf-8")
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not read {project_path}: {e}")

    # 2. Try base template
    template_path = TEMPLATES_DIR / f"{name}.template.md"
    if template_path.exists():
        try:
            return template_path.read_text(encoding="utf-8")
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not read {template_path}: {e}")

    raise FileNotFoundError(
        f"Prompt '{name}' not found in:\n"
        f"  - Project: {project_dir / 'prompts' if project_dir else 'N/A'}\n"
        f"  - Templates: {TEMPLATES_DIR}"
    )


def get_initializer_prompt(project_dir: Path | None = None) -> str:
    """Load the initializer prompt (project-specific if available)."""
    return load_prompt("initializer_prompt", project_dir)


def get_injected_context(project_dir: Path | None = None) -> str | None:
    """
    Load injected context from .agent_context.md if it exists.

    This file is created by the assistant's agent_inject_context tool
    to provide hints or instructions to the coding agent.

    Args:
        project_dir: The project directory

    Returns:
        The injected context content, or None if no context file exists
    """
    if not project_dir:
        return None

    context_file = project_dir / ".agent_context.md"
    if not context_file.exists():
        return None

    try:
        content = context_file.read_text(encoding="utf-8").strip()
        return content if content else None
    except (OSError, PermissionError):
        return None


def get_handover_notes(project_dir: Path | None = None) -> str | None:
    """
    Load handover notes from .agent_handover.md if they exist.

    Handover notes are generated when a session ends to help the next
    session pick up where it left off.

    Args:
        project_dir: The project directory

    Returns:
        The handover notes content, or None if no handover file exists
    """
    if not project_dir:
        return None

    handover_file = project_dir / ".agent_handover.md"
    if not handover_file.exists():
        return None

    try:
        content = handover_file.read_text(encoding="utf-8").strip()
        return content if content else None
    except (OSError, PermissionError):
        return None


def get_coding_prompt(project_dir: Path | None = None) -> str:
    """Load the coding agent prompt (project-specific if available)."""
    prompt = load_prompt("coding_prompt", project_dir)

    # Append handover notes from previous session if available
    handover = get_handover_notes(project_dir)
    if handover:
        prompt += f"\n\n---\n\n## Handover Notes from Previous Session\n\nThe previous session generated these notes to help you continue:\n\n{handover}\n"

    # Append injected context if available
    context = get_injected_context(project_dir)
    if context:
        prompt += f"\n\n---\n\n## Injected Context from Assistant\n\nThe project assistant has provided the following context/instructions:\n\n{context}\n"

    return prompt


def get_coding_prompt_yolo(project_dir: Path | None = None) -> str:
    """Load the YOLO mode coding agent prompt (project-specific if available)."""
    prompt = load_prompt("coding_prompt_yolo", project_dir)

    # Append handover notes from previous session if available
    handover = get_handover_notes(project_dir)
    if handover:
        prompt += f"\n\n---\n\n## Handover Notes from Previous Session\n\nThe previous session generated these notes to help you continue:\n\n{handover}\n"

    # Append injected context if available
    context = get_injected_context(project_dir)
    if context:
        prompt += f"\n\n---\n\n## Injected Context from Assistant\n\nThe project assistant has provided the following context/instructions:\n\n{context}\n"

    return prompt


def get_decomposition_prompt(project_dir: Path | None, stuck_feature: dict | None = None) -> str:
    """
    Generate a prompt for decomposing a stuck feature into smaller sub-features.

    This is called when a feature has been attempted multiple times without success.
    The agent will analyze the feature and break it into smaller, more manageable pieces.

    Args:
        project_dir: The project directory
        stuck_feature: Dictionary with stuck feature details (id, name, description, steps, attempts)

    Returns:
        The decomposition prompt string
    """
    if not stuck_feature:
        stuck_feature = {
            "id": "unknown",
            "name": "Unknown Feature",
            "description": "No description available",
            "steps": [],
            "attempts": 0,
        }

    steps_text = "\n".join(f"  - {step}" for step in stuck_feature.get("steps", []))

    prompt = f'''# Feature Decomposition Mode

## What Happened
Feature #{stuck_feature["id"]} has been attempted {stuck_feature.get("attempts", "multiple")} times without successfully passing.
This indicates the feature is too complex to implement in one go.

## The Stuck Feature
**Name:** {stuck_feature["name"]}
**Category:** {stuck_feature.get("category", "Unknown")}
**Description:** {stuck_feature["description"]}
**Steps:**
{steps_text}

## Your Task
You must decompose this complex feature into **2-5 smaller sub-features** that are each easier to implement and test independently.

### Guidelines for Decomposition:
1. **Analyze the failure** - First understand WHY the feature kept failing:
   - Is there a dependency on another feature not yet implemented?
   - Is the scope too broad (trying to do too many things)?
   - Are there edge cases or error handling making it complex?
   - Is the test criteria unclear or too strict?

2. **Break it down logically** - Each sub-feature should:
   - Be independently testable
   - Have a clear, single responsibility
   - Build on previous sub-features if needed
   - Be small enough to implement in one session

3. **Common decomposition strategies**:
   - **By layer**: UI component → API integration → State management
   - **By functionality**: Basic flow → Validation → Error handling → Edge cases
   - **By scope**: Core feature → Optional enhancements → Polish
   - **By dependency**: Independent pieces first → Dependent pieces later

## Required Action
Use the `feature_decompose` tool to break this feature into sub-features.

Example:
```
feature_decompose(
    feature_id={stuck_feature["id"]},
    sub_features=[
        {{
            "name": "Feature Name - Part 1 (Basic)",
            "description": "What this sub-feature accomplishes",
            "steps": ["Step 1", "Step 2", "Verify step"]
        }},
        {{
            "name": "Feature Name - Part 2 (Enhanced)",
            "description": "What this sub-feature adds",
            "steps": ["Step 1", "Step 2", "Verify step"]
        }}
    ],
    reason="Explanation of why decomposition was needed"
)
```

## After Decomposition
- The original feature will be marked as "decomposed"
- Sub-features will be added to the queue right after the parent
- When ALL sub-features pass, the parent will automatically pass
- You can then continue implementing the first sub-feature

## Important Notes
- Do NOT skip this feature - decompose it instead
- Each sub-feature should be achievable in a single agent session
- Sub-feature names should clearly indicate they are part of the parent
- The steps should be specific and testable
'''

    # Append any injected context
    context = get_injected_context(project_dir)
    if context:
        prompt += f"\n\n---\n\n## Additional Context from Assistant\n\n{context}\n"

    return prompt


def get_app_spec(project_dir: Path) -> str:
    """
    Load the app spec from the project.

    Checks in order:
    1. Project prompts directory: {project_dir}/prompts/app_spec.txt
    2. Project root (legacy): {project_dir}/app_spec.txt

    Args:
        project_dir: The project directory

    Returns:
        The app spec content

    Raises:
        FileNotFoundError: If no app_spec.txt found
    """
    # Try project prompts directory first
    project_prompts = get_project_prompts_dir(project_dir)
    spec_path = project_prompts / "app_spec.txt"
    if spec_path.exists():
        try:
            return spec_path.read_text(encoding="utf-8")
        except (OSError, PermissionError) as e:
            raise FileNotFoundError(f"Could not read {spec_path}: {e}") from e

    # Fallback to legacy location in project root
    legacy_spec = project_dir / "app_spec.txt"
    if legacy_spec.exists():
        try:
            return legacy_spec.read_text(encoding="utf-8")
        except (OSError, PermissionError) as e:
            raise FileNotFoundError(f"Could not read {legacy_spec}: {e}") from e

    raise FileNotFoundError(f"No app_spec.txt found for project: {project_dir}")


def scaffold_project_prompts(project_dir: Path) -> Path:
    """
    Create the project prompts directory and copy base templates.

    This sets up a new project with template files that can be customized.

    Args:
        project_dir: The absolute path to the project directory

    Returns:
        The path to the project prompts directory
    """
    project_prompts = get_project_prompts_dir(project_dir)
    project_prompts.mkdir(parents=True, exist_ok=True)

    # Define template mappings: (source_template, destination_name)
    templates = [
        ("app_spec.template.txt", "app_spec.txt"),
        ("coding_prompt.template.md", "coding_prompt.md"),
        ("coding_prompt_yolo.template.md", "coding_prompt_yolo.md"),
        ("initializer_prompt.template.md", "initializer_prompt.md"),
    ]

    copied_files = []
    for template_name, dest_name in templates:
        template_path = TEMPLATES_DIR / template_name
        dest_path = project_prompts / dest_name

        # Only copy if template exists and destination doesn't
        if template_path.exists() and not dest_path.exists():
            try:
                shutil.copy(template_path, dest_path)
                copied_files.append(dest_name)
            except (OSError, PermissionError) as e:
                print(f"  Warning: Could not copy {dest_name}: {e}")

    if copied_files:
        print(f"  Created prompt files: {', '.join(copied_files)}")

    return project_prompts


def has_project_prompts(project_dir: Path) -> bool:
    """
    Check if a project has valid prompts set up.

    A project has valid prompts if:
    1. The prompts directory exists, AND
    2. app_spec.txt exists within it, AND
    3. app_spec.txt contains the <project_specification> tag

    Args:
        project_dir: The project directory to check

    Returns:
        True if valid project prompts exist, False otherwise
    """
    project_prompts = get_project_prompts_dir(project_dir)
    app_spec = project_prompts / "app_spec.txt"

    if not app_spec.exists():
        # Also check legacy location in project root
        legacy_spec = project_dir / "app_spec.txt"
        if legacy_spec.exists():
            try:
                content = legacy_spec.read_text(encoding="utf-8")
                return "<project_specification>" in content
            except (OSError, PermissionError):
                return False
        return False

    # Check for valid spec content
    try:
        content = app_spec.read_text(encoding="utf-8")
        return "<project_specification>" in content
    except (OSError, PermissionError):
        return False


def copy_spec_to_project(project_dir: Path) -> None:
    """
    Copy the app spec file into the project root directory for the agent to read.

    This maintains backwards compatibility - the agent expects app_spec.txt
    in the project root directory.

    The spec is sourced from: {project_dir}/prompts/app_spec.txt

    Args:
        project_dir: The project directory
    """
    spec_dest = project_dir / "app_spec.txt"

    # Don't overwrite if already exists
    if spec_dest.exists():
        return

    # Copy from project prompts directory
    project_prompts = get_project_prompts_dir(project_dir)
    project_spec = project_prompts / "app_spec.txt"
    if project_spec.exists():
        try:
            shutil.copy(project_spec, spec_dest)
            print("Copied app_spec.txt to project directory")
            return
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not copy app_spec.txt: {e}")
            return

    print("Warning: No app_spec.txt found to copy to project directory")
