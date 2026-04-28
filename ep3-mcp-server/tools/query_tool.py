"""query_tool.py — SELECT-only SQLite query tool.

Design principles demonstrated:
  1. Guard at the boundary — SELECT check + read-only DB connection happen
     before any data is touched. The model cannot instruct the tool to skip them.
  2. Read-only enforcement at the DB level — sqlite3 URI mode=ro means write
     operations fail at the filesystem layer, not just the application layer.
  3. Explicit error returns — never raises. All failures return a JSON error
     object so Claude receives a parseable, predictable response.
  4. Structured JSON output — rows returned as an array of column-name dicts.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# SQL tokens that are safe to execute.
# WITH is allowed for CTEs, but write-safety is enforced at the DB level
# (mode=ro), not by token matching alone.
ALLOWED_FIRST_TOKENS = frozenset({"SELECT", "WITH", "EXPLAIN", "PRAGMA"})


def query_db(sql: str, db_path: Path) -> str:
    """Run a read-only query against the SQLite database at db_path.

    Args:
        sql:     A SQL query string. SELECT, WITH, EXPLAIN, and PRAGMA allowed.
        db_path: Absolute path to the SQLite database file.

    Returns:
        JSON string — one of:
          [{"col": val, ...}, ...]   on success
          {"error": "message"}       on any failure
    """
    sql_stripped = sql.strip()
    if not sql_stripped:
        return json.dumps({"error": "Empty query"})

    first_token = sql_stripped.split()[0].upper()
    if first_token not in ALLOWED_FIRST_TOKENS:
        return json.dumps({
            "error": f"Only SELECT queries are allowed. Got: {first_token}. "
                     "Write operations are not permitted through this tool."
        })

    if not db_path.exists():
        return json.dumps({
            "error": f"Database not found: {db_path}. "
                     "Run create_db.py to bootstrap the sample database."
        })

    try:
        # mode=ro opens the database in read-only mode at the OS level.
        # Any write attempt (even via a WITH ... DELETE CTE) raises OperationalError.
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql_stripped)
        rows = cur.fetchall()
        conn.close()

        if cur.description is None:
            return json.dumps([])

        return json.dumps([dict(row) for row in rows])

    except sqlite3.OperationalError as e:
        return json.dumps({"error": f"Query error: {e}"})
    except sqlite3.DatabaseError as e:
        return json.dumps({"error": f"Database error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})
