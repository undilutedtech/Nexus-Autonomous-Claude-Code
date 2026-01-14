"""
Agent Session Logic
===================

Core agent interaction functions for running autonomous coding sessions.
"""

import asyncio
import io
import sys
from pathlib import Path
from typing import Optional

from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import ResultMessage

# Fix Windows console encoding for Unicode characters (emoji, etc.)
# Without this, print() crashes when Claude outputs emoji like ✅
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from client import create_client
from progress import (
    AUTO_CONTINUE_DELAY,
    check_completion_status,
    clear_feature_attempt,
    clear_pending_decomposition,
    count_passing_tests,
    get_current_feature_id,
    get_pending_decomposition,
    get_stuck_feature_details,
    has_features,
    print_progress_summary,
    print_session_header,
    record_feature_attempt,
    reset_stuck_detection,
    send_agent_status_webhook,
)
from handover import clear_handover_notes, create_handover_on_exit
from prompts import (
    copy_spec_to_project,
    get_coding_prompt,
    get_coding_prompt_yolo,
    get_decomposition_prompt,
    get_handover_notes,
    get_initializer_prompt,
)
from usage_tracking import (
    check_usage_limits,
    print_session_usage,
    print_usage_summary,
    record_session_usage,
)


async def run_agent_session(
    client: ClaudeSDKClient,
    message: str,
    project_dir: Path,
    model: str,
) -> tuple[str, str, dict | None]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path
        model: Model being used (for cost calculation)

    Returns:
        (status, response_text, result_data) where:
        - status: "continue" if agent should continue working, "error" if error
        - response_text: The assistant's text response
        - result_data: Dictionary with usage data from ResultMessage (or None)
    """
    print("Sending prompt to Claude Agent SDK...\n")

    result_data = None

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        async for msg in client.receive_response():
            # Check for ResultMessage (contains usage data)
            if isinstance(msg, ResultMessage):
                result_data = {
                    "session_id": msg.session_id,
                    "usage": msg.usage,
                    "total_cost_usd": msg.total_cost_usd,
                    "duration_ms": msg.duration_ms,
                    "duration_api_ms": msg.duration_api_ms,
                    "num_turns": msg.num_turns,
                    "is_error": msg.is_error,
                }
                continue

            msg_type = type(msg).__name__

            # Handle AssistantMessage (text and tool use)
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        print(f"\n[Tool: {block.name}]", flush=True)
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"   Input: {input_str[:200]}...", flush=True)
                            else:
                                print(f"   Input: {input_str}", flush=True)

            # Handle UserMessage (tool results)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        # Check if command was blocked by security hook
                        if "blocked" in str(result_content).lower():
                            print(f"   [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            # Show errors (truncated)
                            error_str = str(result_content)[:500]
                            print(f"   [Error] {error_str}", flush=True)
                        else:
                            # Tool succeeded - just show brief confirmation
                            print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")

        # Record usage if we have result data
        if result_data:
            session_usage = record_session_usage(
                project_dir=project_dir,
                session_id=result_data.get("session_id", "unknown"),
                model=model,
                usage=result_data.get("usage"),
                total_cost_usd=result_data.get("total_cost_usd"),
                duration_ms=result_data.get("duration_ms", 0),
                duration_api_ms=result_data.get("duration_api_ms", 0),
                num_turns=result_data.get("num_turns", 0),
            )
            print_session_usage(session_usage)

        return "continue", response_text, result_data

    except Exception as e:
        print(f"Error during agent session: {e}")
        return "error", str(e), None


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
    yolo_mode: bool = False,
) -> None:
    """
    Run the autonomous agent loop.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        max_iterations: Maximum number of iterations (None for unlimited)
        yolo_mode: If True, skip browser testing and use YOLO prompt
    """
    print("\n" + "=" * 70)
    print("  AUTONOMOUS CODING AGENT DEMO")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print(f"Model: {model}")
    if yolo_mode:
        print("Mode: YOLO (testing disabled)")
    else:
        print("Mode: Standard (full testing)")
    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited (will run until completion)")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Check if this is a fresh start or continuation
    # Uses has_features() which checks if the database actually has features,
    # not just if the file exists (empty db should still trigger initializer)
    is_first_run = not has_features(project_dir)

    if is_first_run:
        print("Fresh start - will use initializer agent")
        print()
        print("=" * 70)
        print("  NOTE: First session takes 10-20+ minutes!")
        print("  The agent is generating 200 detailed test cases.")
        print("  This may appear to hang - it's working. Watch for [Tool: ...] output.")
        print("=" * 70)
        print()
        # Copy the app spec into the project directory for the agent to read
        copy_spec_to_project(project_dir)
        # Send agent started notification
        send_agent_status_webhook(
            project_dir, "started",
            reason="Fresh project initialization started",
            details={"mode": "initializer", "yolo_mode": yolo_mode}
        )
    else:
        print("Continuing existing project")
        print_progress_summary(project_dir)
        # Send agent started notification
        send_agent_status_webhook(
            project_dir, "started",
            reason="Resuming existing project",
            details={"mode": "coding", "yolo_mode": yolo_mode}
        )

    # Main loop
    iteration = 0
    completion_reason = None

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break

        # Check for completion BEFORE starting a new session (skip on first run)
        decomposition_mode = False
        if not is_first_run:
            should_stop, reason, action = check_completion_status(project_dir)
            if action == "decompose":
                # Feature is stuck - enter decomposition mode instead of stopping
                decomposition_mode = True
                stuck_feature = get_stuck_feature_details(project_dir)
                print(f"\n{'=' * 70}")
                print(f"  AUTOMATIC DECOMPOSITION MODE")
                print(f"{'=' * 70}")
                print()
                print(f"  REASON: Feature has been attempted multiple times without success.")
                if stuck_feature:
                    print(f"  STUCK FEATURE: #{stuck_feature['id']} - {stuck_feature['name']}")
                    print(f"  ATTEMPTS: {stuck_feature.get('attempts', 'unknown')}")
                print()
                print(f"  ACTION: The agent will automatically break this complex feature")
                print(f"          into smaller, more manageable sub-tasks.")
                print()
                print(f"  HOW IT WORKS:")
                print(f"    1. Agent analyzes why the feature is failing")
                print(f"    2. Creates 2-5 smaller sub-features from the original")
                print(f"    3. Sub-features are added to the queue right after the parent")
                print(f"    4. When all sub-features pass, the parent auto-completes")
                print()
                print(f"  This prevents the agent from getting permanently stuck!")
                print(f"{'=' * 70}")
                send_agent_status_webhook(
                    project_dir, "decomposing",
                    reason=f"Feature #{stuck_feature['id'] if stuck_feature else '?'} stuck after multiple attempts. Auto-decomposing into smaller tasks.",
                    details={
                        "stuck_feature": stuck_feature,
                        "action": "decomposition",
                        "explanation": "Agent will break this feature into smaller sub-tasks that are easier to implement."
                    }
                )
            elif should_stop:
                completion_reason = reason
                print(f"\n{'=' * 70}")
                print(f"  COMPLETION DETECTED")
                print(f"{'=' * 70}")
                print(f"\n{reason}")
                # Send appropriate status webhook
                if "passing" in reason.lower():
                    send_agent_status_webhook(project_dir, "complete", reason=reason)
                elif "stuck" in reason.lower():
                    send_agent_status_webhook(project_dir, "stuck", reason=reason)
                else:
                    send_agent_status_webhook(project_dir, "stopped", reason=reason)
                break

        # Check usage limits (cost/token limits) - this also sends warnings
        limit_exceeded, limit_reason = check_usage_limits(project_dir)
        if limit_exceeded:
            completion_reason = limit_reason
            print(f"\n{'=' * 70}")
            print(f"  USAGE LIMIT EXCEEDED")
            print(f"{'=' * 70}")
            print(f"\n{limit_reason}")
            send_agent_status_webhook(
                project_dir, "stopped",
                reason="Usage limit exceeded",
                details={"limit_reason": limit_reason}
            )
            break

        # Track which feature we're working on (for stuck detection)
        feature_id_before = get_current_feature_id(project_dir)
        passing_before, _, _ = count_passing_tests(project_dir)

        # Print session header with progress
        print_session_header(iteration, is_first_run, project_dir)

        # Create client (fresh context)
        client = create_client(project_dir, model, yolo_mode=yolo_mode)

        # Choose prompt based on session type
        # Pass project_dir to enable project-specific prompts
        if is_first_run:
            prompt = get_initializer_prompt(project_dir)
            is_first_run = False  # Only use initializer once
            # Reset stuck detection for fresh project
            reset_stuck_detection(project_dir)
        elif decomposition_mode:
            # Use decomposition prompt when a feature is stuck
            stuck_feature = get_stuck_feature_details(project_dir)
            prompt = get_decomposition_prompt(project_dir, stuck_feature)
            print(f"[Decomposing feature: {stuck_feature['name'] if stuck_feature else 'unknown'}]")
        else:
            # Use YOLO prompt if in YOLO mode
            if yolo_mode:
                prompt = get_coding_prompt_yolo(project_dir)
            else:
                prompt = get_coding_prompt(project_dir)

            # Clear handover notes after first coding session consumes them
            if iteration == 1 and get_handover_notes(project_dir):
                print("[Handover notes from previous session consumed]")
                clear_handover_notes(project_dir)

        # Run session with async context manager
        async with client:
            status, response, result_data = await run_agent_session(client, prompt, project_dir, model)

        # After session: track feature attempts for stuck detection
        passing_after, _, _ = count_passing_tests(project_dir)
        feature_id_after = get_current_feature_id(project_dir)

        # If decomposition mode was active, clear it (decomposition happened)
        if decomposition_mode:
            pending_decomp = get_pending_decomposition(project_dir)
            if pending_decomp:
                # Clear the stuck detection for this feature (it's now decomposed)
                clear_feature_attempt(project_dir, pending_decomp)
                clear_pending_decomposition(project_dir)
                print(f"\n[Feature #{pending_decomp} decomposed into sub-features]")

        # If a feature was in progress and is now passing, clear its attempt count
        if feature_id_before and passing_after > passing_before:
            clear_feature_attempt(project_dir, feature_id_before)

        # If still working on the same feature (not passed), record the attempt
        if feature_id_after and feature_id_after == feature_id_before:
            attempt_count = record_feature_attempt(project_dir, feature_id_after)
            if attempt_count > 1:
                print(f"\n[Attempt #{attempt_count} for feature #{feature_id_after}]")

        # Handle status
        if status == "continue":
            print(f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY}s...")
            print_progress_summary(project_dir)

            # Check completion after printing progress
            should_stop, reason, action = check_completion_status(project_dir)
            if action == "decompose":
                # Will trigger decomposition in next iteration
                print(f"\n[Feature stuck - will decompose in next session]")
            elif should_stop:
                completion_reason = reason
                print(f"\n{'=' * 70}")
                print(f"  COMPLETION DETECTED")
                print(f"{'=' * 70}")
                print(f"\n{reason}")
                # Send appropriate status webhook
                if "passing" in reason.lower():
                    send_agent_status_webhook(project_dir, "complete", reason=reason)
                elif "stuck" in reason.lower():
                    send_agent_status_webhook(project_dir, "stuck", reason=reason)
                else:
                    send_agent_status_webhook(project_dir, "stopped", reason=reason)
                break

            await asyncio.sleep(AUTO_CONTINUE_DELAY)

        elif status == "error":
            print("\nSession encountered an error")
            print("Will retry with a fresh session...")
            send_agent_status_webhook(
                project_dir, "error",
                reason="Session encountered an error, will retry",
                details={"iteration": iteration}
            )
            await asyncio.sleep(AUTO_CONTINUE_DELAY)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\nPreparing next session...\n")
            await asyncio.sleep(1)

    # Generate handover notes for next session (unless project is complete)
    if not (completion_reason and "All" in completion_reason and "passing" in completion_reason):
        reason = completion_reason or f"Session ended after {iteration} iterations"
        create_handover_on_exit(project_dir, reason, iteration)

    # Final summary
    print("\n" + "=" * 70)
    if completion_reason and "All" in completion_reason and "passing" in completion_reason:
        print("  PROJECT COMPLETE!")
    elif completion_reason and "stuck" in completion_reason.lower():
        print("  AGENT STOPPED (STUCK DETECTED)")
    elif completion_reason and "limit" in completion_reason.lower():
        print("  AGENT STOPPED (USAGE LIMIT EXCEEDED)")
    else:
        print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print_progress_summary(project_dir)
    print_usage_summary(project_dir)

    # Show completion-specific messaging
    if completion_reason:
        if "All" in completion_reason and "passing" in completion_reason:
            print("\n" + "-" * 70)
            print("  CONGRATULATIONS! All features are implemented!")
            print("-" * 70)
            print("\n  Your application is ready to run.")
        elif "stuck" in completion_reason.lower():
            print("\n" + "-" * 70)
            print("  AGENT STOPPED DUE TO STUCK DETECTION")
            print("-" * 70)
            print("\n  The agent attempted a feature multiple times without success.")
            print("  Options:")
            print("    1. Review the feature and simplify it")
            print("    2. Use feature_skip to move to the next feature")
            print("    3. Increase NEXUS_MAX_FEATURE_ATTEMPTS env var")
            print("    4. Re-run the agent to retry")
        elif "limit" in completion_reason.lower():
            print("\n" + "-" * 70)
            print("  AGENT STOPPED DUE TO USAGE LIMITS")
            print("-" * 70)
            print("\n  The agent exceeded configured cost or token limits.")
            print("  Options:")
            print("    1. Increase NEXUS_MAX_COST_USD env var (current limit reached)")
            print("    2. Increase NEXUS_MAX_TOKENS env var (current limit reached)")
            print("    3. Set limits to 0 for unlimited usage")
            print("    4. Re-run the agent to continue (new session starts fresh tracking)")

    # Print instructions for running the generated application
    print("\n" + "-" * 70)
    print("  TO RUN THE GENERATED APPLICATION:")
    print("-" * 70)
    print(f"\n  cd {project_dir.resolve()}")
    print("  ./init.sh           # Run the setup script")
    print("  # Or manually:")
    print("  npm install && npm run dev")
    print("\n  Then open http://localhost:3000 (or check init.sh for the URL)")
    print("-" * 70)

    print("\nDone!")
