# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an autonomous coding agent system with a React-based UI. It uses the Claude Agent SDK to build complete applications over multiple sessions using a two-agent pattern:

1. **Initializer Agent** - First session reads an app spec and creates features in a SQLite database
2. **Coding Agent** - Subsequent sessions implement features one by one, marking them as passing

## Commands

### Quick Start (Recommended)

```bash
# Windows - launches CLI menu
start.bat

# macOS/Linux
./start.sh

# Launch Web UI (serves pre-built React app)
start_ui.bat      # Windows
./start_ui.sh     # macOS/Linux
```

### Python Backend (Manual)

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the main CLI launcher
python start.py

# Run agent directly for a project (use absolute path or registered name)
python autonomous_agent_demo.py --project-dir C:/Projects/my-app
python autonomous_agent_demo.py --project-dir my-app  # if registered

# YOLO mode: rapid prototyping without browser testing
python autonomous_agent_demo.py --project-dir my-app --yolo
```

### YOLO Mode (Rapid Prototyping)

YOLO mode skips all testing for faster feature iteration:

```bash
# CLI
python autonomous_agent_demo.py --project-dir my-app --yolo

# UI: Toggle the lightning bolt button before starting the agent
```

**What's different in YOLO mode:**
- No regression testing (skips `feature_get_for_regression`)
- No Playwright MCP server (browser automation disabled)
- Features marked passing after lint/type-check succeeds
- Faster iteration for prototyping

**What's the same:**
- Lint and type-check still run to verify code compiles
- Feature MCP server for tracking progress
- All other development tools available

**When to use:** Early prototyping when you want to quickly scaffold features without verification overhead. Switch back to standard mode for production-quality development.

### React UI (in ui/ directory)

```bash
cd ui
npm install
npm run dev      # Development server (hot reload)
npm run build    # Production build (required for start_ui.bat)
npm run lint     # Run ESLint
```

**Note:** The `start_ui.bat` script serves the pre-built UI from `ui/dist/`. After making UI changes, run `npm run build` in the `ui/` directory.

## Architecture

### Core Python Modules

- `start.py` - CLI launcher with project creation/selection menu
- `autonomous_agent_demo.py` - Entry point for running the agent
- `agent.py` - Agent session loop using Claude Agent SDK
- `client.py` - ClaudeSDKClient configuration with security hooks and MCP servers
- `security.py` - Bash command allowlist validation (ALLOWED_COMMANDS whitelist)
- `prompts.py` - Prompt template loading with project-specific fallback
- `progress.py` - Progress tracking, database queries, webhook notifications
- `registry.py` - Project registry for mapping names to paths (cross-platform)
- `usage_tracking.py` - Token usage and cost tracking across agent sessions

### Project Registry

Projects can be stored in any directory. The registry maps project names to paths using SQLite:
- **All platforms**: `~/.nexus/registry.db`

The registry uses:
- SQLite database with SQLAlchemy ORM
- POSIX path format (forward slashes) for cross-platform compatibility
- SQLite's built-in transaction handling for concurrency safety

### Server API (server/)

The FastAPI server provides REST endpoints for the UI:

- `server/routers/projects.py` - Project CRUD with registry integration
- `server/routers/features.py` - Feature management
- `server/routers/agent.py` - Agent control (start/stop/pause/resume)
- `server/routers/filesystem.py` - Filesystem browser API with security controls
- `server/routers/spec_creation.py` - WebSocket for interactive spec creation

### Feature Management

Features are stored in SQLite (`features.db`) via SQLAlchemy. The agent interacts with features through an MCP server:

- `mcp_server/feature_mcp.py` - MCP server exposing feature management tools
- `api/database.py` - SQLAlchemy models (Feature table with priority, category, name, description, steps, passes)

MCP tools available to the agent:
- `feature_get_stats` - Progress statistics
- `feature_get_next` - Get highest-priority pending feature
- `feature_get_for_regression` - Random passing features for regression testing
- `feature_mark_passing` - Mark feature complete
- `feature_skip` - Move feature to end of queue
- `feature_create_bulk` - Initialize all features (used by initializer)

### Assistant Chat with Agent Control

The assistant chat (`server/services/assistant_chat_session.py`) provides a conversational interface that can:
- Read and analyze project files
- Answer questions about the codebase
- **Control the coding agent** via MCP tools

Agent control MCP server (`mcp_server/agent_control_mcp.py`) provides:
- `agent_get_status` - Check if agent is running/paused/stopped
- `agent_start` - Start the coding agent (with optional YOLO mode)
- `agent_stop` - Stop the coding agent
- `agent_pause` - Pause the agent
- `agent_resume` - Resume a paused agent
- `agent_skip_feature` - Skip a problematic feature
- `agent_clear_stuck` - Clear in-progress status of stuck features
- `agent_inject_context` - Add context/instructions for the agent
- `agent_clear_context` - Clear injected context
- `agent_get_progress` - Get detailed progress statistics
- `agent_reset_stuck_detection` - Reset attempt tracking

Context injection writes to `{project_dir}/.agent_context.md` which the agent can read.

### Local Skill Invocation

The skill MCP server (`mcp_server/skill_mcp.py`) allows agents to discover and use local skills:

**Skill sources (in priority order):**
1. Project-specific: `{project_dir}/.claude/skills/`
2. Nexus root: `{nexus_root}/.claude/skills/`

**Skill tools:**
- `skill_list` - List all available skills
- `skill_get` - Get full content of a skill
- `skill_invoke` - Invoke a skill with optional context
- `skill_create` - Create a new project-specific skill

**Command tools:**
- `command_list` - List all available commands
- `command_get` - Get full content of a command
- `command_invoke` - Invoke a command with optional args

**Skill file format** (`SKILL.md`):
```yaml
---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces
---

# Skill content in markdown...
```

Skills provide specialized guidelines that agents follow for specific tasks (e.g., UI design, code patterns).

### Nuxt.js Documentation MCP

The Nuxt MCP server (`https://nuxt.com/mcp`) provides access to Nuxt.js documentation:

**Documentation tools:**
- `list_documentation_pages` - List all available Nuxt docs pages
- `get_documentation_page` - Get content of a specific page
- `get_getting_started_guide` - Get version-specific getting started guide

**Blog tools:**
- `list_blog_posts` - List Nuxt blog posts
- `get_blog_post` - Get content of a blog post

**Deployment tools:**
- `list_deploy_providers` - List supported hosting platforms
- `get_deploy_provider` - Get deployment instructions for a provider

**Guided prompts:**
- `find_documentation_for_topic` - Search docs by topic
- `deployment_guide` - Get deployment guidance
- `migration_help` - Get migration assistance

This enables agents to access up-to-date Nuxt.js documentation when building Nuxt applications.

### React UI (ui/)

- Tech stack: React 18, TypeScript, TanStack Query, Tailwind CSS v4, Radix UI
- `src/App.tsx` - Main app with project selection, kanban board, agent controls
- `src/hooks/useWebSocket.ts` - Real-time updates via WebSocket
- `src/hooks/useProjects.ts` - React Query hooks for API calls
- `src/lib/api.ts` - REST API client
- `src/lib/types.ts` - TypeScript type definitions
- `src/components/FolderBrowser.tsx` - Server-side filesystem browser for project folder selection
- `src/components/NewProjectModal.tsx` - Multi-step project creation wizard

### Project Structure for Generated Apps

Projects can be stored in any directory (registered in `~/.nexus/registry.db`). Each project contains:
- `prompts/app_spec.txt` - Application specification (XML format)
- `prompts/initializer_prompt.md` - First session prompt
- `prompts/coding_prompt.md` - Continuation session prompt
- `features.db` - SQLite database with feature test cases
- `.agent.lock` - Lock file to prevent multiple agent instances

### Security Model

Defense-in-depth approach configured in `client.py`:
1. OS-level sandbox for bash commands
2. Filesystem restricted to project directory only
3. Bash commands validated against `ALLOWED_COMMANDS` in `security.py`

## Claude Code Integration

- `.claude/commands/create-spec.md` - `/create-spec` slash command for interactive spec creation
- `.claude/skills/frontend-design/SKILL.md` - Skill for distinctive UI design
- `.claude/templates/` - Prompt templates copied to new projects

## Key Patterns

### Prompt Loading Fallback Chain

1. Project-specific: `{project_dir}/prompts/{name}.md`
2. Base template: `.claude/templates/{name}.template.md`

### Agent Session Flow

1. Check if `features.db` has features (determines initializer vs coding agent)
2. Create ClaudeSDKClient with security settings
3. Send prompt and stream response
4. Check for completion (all features passing) or stuck detection
5. Auto-continue with configurable delay between sessions (default: 3 seconds)
6. Stop automatically when all features pass or agent is stuck

### Completion Detection

The agent automatically stops when:
- **All features passing**: All features in the database are marked as passing
- **Stuck detection**: A feature has been attempted `NEXUS_MAX_FEATURE_ATTEMPTS` times (default: 3) without passing
- **Usage limits exceeded**: Cost or token limits have been reached

Files used for tracking:
- `.feature_attempts` - JSON file tracking attempt counts per feature ID
- `.usage_stats.json` - JSON file tracking token usage and costs per session

### Usage Tracking

The `usage_tracking.py` module tracks token usage and costs across agent sessions:

**Features:**
- Per-session tracking of input/output tokens, cache usage, costs, duration
- Cumulative statistics across all sessions
- Configurable cost and token limits to prevent runaway usage
- Model-specific pricing (Opus 4.5, Sonnet 4.5, Sonnet 4, Haiku 3.5)

**How it works:**
1. Each agent session captures token usage from Claude's `ResultMessage`
2. Cost is calculated using model-specific pricing (or provided by the API)
3. Usage is appended to `.usage_stats.json` in the project directory
4. Before each session, limits are checked and agent stops if exceeded

**Usage summary displayed:**
- Total tokens (input + output)
- Cache tokens (read + creation)
- Total cost in USD
- Duration and turn counts
- Remaining budget (if limits configured)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXUS_AUTO_CONTINUE_DELAY` | `3` | Seconds to wait between agent sessions |
| `NEXUS_MAX_FEATURE_ATTEMPTS` | `3` | Max attempts per feature before stuck detection triggers |
| `NEXUS_MAX_COST_USD` | `0` | Maximum cost in USD before stopping (0 = unlimited) |
| `NEXUS_MAX_TOKENS` | `0` | Maximum total tokens before stopping (0 = unlimited) |
| `PROGRESS_N8N_WEBHOOK_URL` | (none) | Webhook URL for progress notifications |

### Real-time UI Updates

The UI receives updates via WebSocket (`/ws/projects/{project_name}`):
- `progress` - Test pass counts
- `agent_status` - Running/paused/stopped/crashed
- `log` - Agent output lines (streamed from subprocess stdout)
- `feature_update` - Feature status changes

### Design System

The UI uses a **neobrutalism** design with Tailwind CSS v4:
- CSS variables defined in `ui/src/styles/globals.css` via `@theme` directive
- Custom animations: `animate-slide-in`, `animate-pulse-neo`, `animate-shimmer`
- Color tokens: `--color-neo-pending` (yellow), `--color-neo-progress` (cyan), `--color-neo-done` (green)
