#!/bin/bash
# Notification hook: compaction_save.sh
#
# Fires on Notification:PreCompact — just before Claude Code summarises the
# context window. Appends a timestamped compaction marker to task_state.md so
# the session history is recoverable.
#
# IMPORTANT: Notification hooks receive data via ENVIRONMENT VARIABLES, not
# stdin. Reading stdin in a Notification hook will hang or read nothing.
# This is the single most common reason Notification hooks silently fail.
#
# Wire this hook in .claude/settings.json:
#   { "event": "Notification", "matcher": "PreCompact", "command": "/abs/path/to/compaction_save.sh" }
#
# Exit 0: always — this hook observes, it does not block.

set -uo pipefail

# Notification data comes from env vars.
EVENT_TYPE="${CLAUDE_NOTIFICATION_TYPE:-}"

if [ "$EVENT_TYPE" != "PreCompact" ]; then
    # Not the event we care about — allow and exit cleanly.
    exit 0
fi

# Write to task_state.md in the current working directory (the project root).
STATE_FILE="task_state.md"

# Create the file if it does not exist yet.
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << 'EOF'
# Task State

<!-- This file is maintained by Claude during the session.
     The compaction_save.sh hook appends a marker whenever the context
     is compacted. Read this file at the start of a new session to resume. -->

## Current task
(not yet written — Claude should update this as work progresses)

## Done
(none yet)

## Next step
(not yet written)

## Blockers / open decisions
(none)
EOF
fi

# Append a compaction marker.
{
    echo ""
    echo "---"
    echo "## Compaction checkpoint: $(date -u '+%Y-%m-%d %H:%M UTC')"
    echo "Context was summarised at this point."
    echo "State above is the last checkpoint before compaction."
} >> "$STATE_FILE"

exit 0
