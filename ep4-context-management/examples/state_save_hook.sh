#!/bin/bash
# Notification hook: state_save_hook.sh
#
# Purpose: Timestamps task_state.md before Claude Code compacts the context window.
#
# When: Notification event, matcher "PreCompact"
#
# What it does:
#   1. Confirms the event is PreCompact (Notification hooks can fire for other events too)
#   2. Appends a timestamped compaction checkpoint to task_state.md
#   3. Writes a one-line diagnostic entry to .claude/compaction_log.txt
#
# What it does NOT do:
#   - Does not edit existing sections of task_state.md (append-only = safe)
#   - Does not block or slow down compaction (always exits 0)
#   - Does not read stdin (Notification hooks use env vars, NOT stdin)
#
# IMPORTANT: Notification hooks receive event data via ENVIRONMENT VARIABLES.
# Reading stdin in a Notification hook hangs silently. This is the single most
# common reason Notification hooks do nothing.
#
# Wire in .claude/settings.json:
#   { "event": "Notification", "matcher": "PreCompact", "command": "/abs/path/to/state_save_hook.sh" }
#
# EP4 vs EP2: This hook is a superset of ep2-hooks/state/compaction_save.sh.
# Use one or the other — do not wire both on the same event.

set -uo pipefail

# Notification data arrives via environment variables.
EVENT_TYPE="${CLAUDE_NOTIFICATION_TYPE:-}"

# Guard: only act on PreCompact — allow all other events through.
if [ "$EVENT_TYPE" != "PreCompact" ]; then
    exit 0
fi

# ── task_state.md ──────────────────────────────────────────────────────────────

STATE_FILE="task_state.md"
TIMESTAMP="$(date -u '+%Y-%m-%d %H:%M UTC')"

# Create task_state.md if it does not exist.
# The hook running at compaction time means a session is active —
# create a minimal file so the post-compaction context has something to read.
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << 'TEMPLATE'
# Task State

## Current Task
(not written — update this with the current task description)

## Done
(nothing recorded yet)

## Next Step
(not written — update this with the next concrete action)

## Open Questions
(none)
TEMPLATE
fi

# Append a compaction marker. Append-only — no section surgery.
{
    printf '\n---\n'
    printf '**Compaction checkpoint: %s**\n' "$TIMESTAMP"
    printf 'Context was summarised at this point. State above reflects the last known step.\n'
} >> "$STATE_FILE"

# ── diagnostic log ─────────────────────────────────────────────────────────────

# Write to .claude/ — this directory is for session tooling state, not source.
# Add .claude/compaction_log.txt to .gitignore.
CLAUDE_DIR=".claude"
LOG_FILE="$CLAUDE_DIR/compaction_log.txt"

mkdir -p "$CLAUDE_DIR"
printf '%s  PreCompact fired\n' "$TIMESTAMP" >> "$LOG_FILE"

# Always exit 0. This hook observes — it does not block.
exit 0
