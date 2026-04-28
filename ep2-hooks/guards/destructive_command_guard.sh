#!/bin/bash
# PreToolUse hook: destructive_command_guard.sh
#
# Intercepts Bash tool calls before execution and blocks commands that match
# a list of destructive patterns. Claude Code shows the exit-2 message to the
# user and stops the agent loop — the command never runs.
#
# Wire this hook in .claude/settings.json:
#   { "event": "PreToolUse", "matcher": "Bash", "command": "/abs/path/to/destructive_command_guard.sh" }
#
# Input: JSON on stdin (PreToolUse passes tool info via stdin, NOT env vars)
# Exit 0: allow the command to run
# Exit 2: block the command — stdout message is shown to the user

set -uo pipefail

# Read the full JSON payload from stdin once and cache it.
INPUT=$(cat)

# Extract the command string. Falls back to empty string if field is missing.
CMD=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null)

# Patterns to block. Case-insensitive match against the full command string.
PATTERNS=(
    "rm -rf"
    "rm -r "
    "rm -r$"
    "git reset --hard"
    "git push --force"
    "git push -f "
    "git push -f$"
    "git push --force-with-lease"
    "DROP TABLE"
    "DROP DATABASE"
    "DROP SCHEMA"
    "TRUNCATE TABLE"
    "TRUNCATE "
    "DELETE FROM"
    "mkfs"
    "dd if="
    "format "
)

for PATTERN in "${PATTERNS[@]}"; do
    if echo "$CMD" | grep -qi "$PATTERN"; then
        echo "⛔ BLOCKED by destructive_command_guard"
        echo "Matched pattern: $PATTERN"
        echo ""
        echo "Command: $CMD"
        echo ""
        echo "If this is intentional, run the command manually in a terminal."
        exit 2
    fi
done

# Explicit exit 0 — never rely on the exit code of the last grep.
exit 0
