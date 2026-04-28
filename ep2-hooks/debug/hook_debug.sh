#!/bin/bash
# hook_debug.sh — universal hook debug template
#
# Logs all hook inputs to /tmp/hook_debug.log so you can see exactly what
# Claude Code is passing to your hooks. Use this as the FIRST step when a
# hook is not working.
#
# Works with all four event types:
#   PreToolUse   — logs stdin JSON (tool name + input)
#   PostToolUse  — logs stdin JSON (tool name + input + output)
#   Notification — logs env vars (CLAUDE_NOTIFICATION_TYPE etc.)
#   Stop         — logs env vars
#
# Wire it temporarily to the event you are debugging:
#   { "event": "PreToolUse", "matcher": "*", "command": "/abs/path/to/hook_debug.sh" }
#   { "event": "Notification", "matcher": "*", "command": "/abs/path/to/hook_debug.sh" }
#
# Always exits 0 — safe to use alongside your real hooks.

LOG_FILE="${HOOK_DEBUG_LOG:-/tmp/hook_debug.log}"
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

{
    echo "========================================"
    echo "Hook fired: $TIMESTAMP"
    echo "Script: $0"
    echo ""

    # Log relevant env vars (Notification hooks pass data here).
    echo "--- Environment variables ---"
    echo "CLAUDE_NOTIFICATION_TYPE : ${CLAUDE_NOTIFICATION_TYPE:-<not set>}"
    echo "CLAUDE_NOTIFICATION_DATA : ${CLAUDE_NOTIFICATION_DATA:-<not set>}"
    echo "CLAUDE_TOOL_NAME         : ${CLAUDE_TOOL_NAME:-<not set>}"
    echo ""

    # Try to read stdin. For Notification hooks stdin is empty — the read
    # will return immediately with nothing. For PreToolUse / PostToolUse
    # it will contain the JSON payload.
    echo "--- stdin ---"
    STDIN_DATA=$(timeout 2 cat 2>/dev/null || true)
    if [ -n "$STDIN_DATA" ]; then
        echo "$STDIN_DATA" | python3 -m json.tool 2>/dev/null || echo "$STDIN_DATA"
    else
        echo "<empty — expected for Notification and Stop hooks>"
    fi
    echo ""
    echo "========================================"
    echo ""
} >> "$LOG_FILE"

# Always allow — this hook only observes.
exit 0
