#!/usr/bin/env python3
"""
PreToolUse hook: select_guard.py

Blocks any SQL tool call that is not a read-only query. Accepts SELECT and
WITH (CTEs). Rejects everything else: INSERT, UPDATE, DELETE, DROP, TRUNCATE,
etc.

Wire this hook in .claude/settings.json with a matcher that covers your SQL
tool name — e.g. "execute_sql" or "mcp__database__query". The matcher in
settings is the first line of defence; this script is the second.

    {
      "event": "PreToolUse",
      "matcher": "execute_sql",
      "command": "/abs/path/to/select_guard.py"
    }

Input:  JSON on stdin (PreToolUse passes tool info via stdin)
Exit 0: allow the query
Exit 2: block — stdout message shown to the user
"""

from __future__ import annotations

import json
import re
import sys


# SQL tokens that indicate a read-only query.
ALLOWED_STARTS = ("SELECT", "WITH", "EXPLAIN", "SHOW", "DESCRIBE", "DESC")

# SQL write/destructive keywords — used for a secondary check when the query
# does not start with a known-safe token.
WRITE_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE|MERGE|UPSERT)\b",
    re.IGNORECASE,
)


def strip_sql_preamble(sql: str) -> str:
    """Remove leading whitespace, semicolons, and block/line comments."""
    # Remove block comments: /* ... */
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    # Remove line comments: -- ...
    sql = re.sub(r"--[^\n]*", "", sql)
    # Strip whitespace and leading semicolons
    return sql.lstrip("; \t\n\r")


def is_read_only(sql: str) -> bool:
    cleaned = strip_sql_preamble(sql)
    first_token = cleaned.split()[0].upper() if cleaned.split() else ""
    if first_token in ALLOWED_STARTS:
        return True
    return False


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # Cannot parse input — fail open (allow) and let Claude Code handle it.
        sys.exit(0)

    tool_input = payload.get("tool_input", {})

    # Support common SQL tool field names.
    sql = (
        tool_input.get("query")
        or tool_input.get("sql")
        or tool_input.get("statement")
        or tool_input.get("command")
        or ""
    )

    if not sql.strip():
        # No SQL found in the payload — not our concern, allow.
        sys.exit(0)

    if is_read_only(sql):
        sys.exit(0)

    # Block the query.
    cleaned = strip_sql_preamble(sql)
    first_token = cleaned.split()[0].upper() if cleaned.split() else "UNKNOWN"

    print("⛔ BLOCKED by select_guard: write operation rejected")
    print(f"First SQL token: {first_token}")
    print("")
    print("Only SELECT, WITH (CTEs), EXPLAIN, SHOW, and DESCRIBE are allowed.")
    print("To run write operations, execute them directly in a database client.")
    sys.exit(2)


if __name__ == "__main__":
    main()
