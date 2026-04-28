#!/bin/bash
# compaction_restore.sh
#
# Reads task_state.md and prints its content to stdout so Claude can
# resume from where the previous session left off.
#
# This is NOT a hook — it is a script you instruct Claude to run at the
# start of a session (or add to your session-start workflow).
#
# Usage:
#   bash compaction_restore.sh
#   bash compaction_restore.sh path/to/task_state.md   # optional custom path
#
# Add this to your global CLAUDE.md or session-start CLAUDE.md:
#   "At the start of every session, run: bash ep2-hooks/state/compaction_restore.sh"

STATE_FILE="${1:-task_state.md}"

echo "========================================"
echo "  SESSION RESUME — reading task_state.md"
echo "========================================"
echo ""

if [ ! -f "$STATE_FILE" ]; then
    echo "No task_state.md found at: $STATE_FILE"
    echo ""
    echo "Start a new task_state.md with:"
    echo "  cp ep2-hooks/state/task_state.md.template task_state.md"
    exit 0
fi

cat "$STATE_FILE"

echo ""
echo "========================================"
echo "  End of task_state.md"
echo "  Review the above and continue the task."
echo "========================================"
