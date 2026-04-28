#!/bin/bash
# PostToolUse hook: test_gate.sh
#
# Fires after a Bash tool call that contains "git commit". Runs the pytest
# test suite and signals a failure if tests are broken.
#
# NOTE: PostToolUse fires AFTER the tool has already run. The commit exists
# by the time this hook fires. Exit 2 cannot undo it — it stops the agent
# loop and surfaces the failure so Claude does not continue building on a
# broken commit. Think of this as an emergency brake, not an undo.
#
# For a true gate that prevents the commit entirely, move this hook to
# PreToolUse. The trade-off: PreToolUse runs BEFORE the commit, so test
# failures will abort commits even when the developer intends a WIP commit.
# PostToolUse is the safer default for most workflows.
#
# Wire this hook in .claude/settings.json:
#   { "event": "PostToolUse", "matcher": "Bash", "command": "/abs/path/to/test_gate.sh", "timeout": 60 }
#   Raise timeout to match your test suite duration.
#
# Input: JSON on stdin (PostToolUse passes tool info via stdin)
# Exit 0: tests pass (or hook does not apply) — agent continues
# Exit 2: tests failing — agent loop stops, failures shown to user

set -uo pipefail

# Read tool info from stdin once and cache it.
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', ''))
except Exception:
    print('')
" 2>/dev/null)

CMD=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null)

# Only act on Bash tool calls.
if [ "$TOOL_NAME" != "Bash" ]; then
    exit 0
fi

# Only act on git commit commands.
if ! echo "$CMD" | grep -q "git commit"; then
    exit 0
fi

# Run the test suite. Capture output to show on failure.
TEST_OUTPUT=$(pytest tests/ -q 2>&1)
TEST_EXIT=$?

if [ $TEST_EXIT -ne 0 ]; then
    echo "❌ Tests failing after commit."
    echo ""
    echo "$TEST_OUTPUT"
    echo ""
    echo "Fix the failing tests before continuing. The commit exists but the"
    echo "agent loop has been stopped to prevent further broken changes."
    exit 2
fi

# Tests pass — agent continues normally.
exit 0
