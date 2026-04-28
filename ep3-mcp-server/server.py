"""server.py — MCP server entry point for ep3-mcp-server.

Registers two tools via FastMCP:
  query_db   — SELECT-only SQLite queries, returns JSON
  read_file  — bounded file reads from the data/ directory

DB path is configured via the DB_PATH environment variable (set in .claude.json).
All tool calls and results are logged to tool_debug.log in this directory.

Usage:
    python server.py            # start via stdio transport (used by Claude Code)
    python test_server.py       # test tools directly without MCP
    python create_db.py         # bootstrap sample.db before first use
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from tools.query_tool import query_db as _query_db
from tools.read_file_tool import read_file as _read_file

# ─── Paths ───────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# DB path: override via DB_PATH env var (set in .claude.json mcpServers env block)
DB_PATH = Path(os.environ.get("DB_PATH", str(DATA_DIR / "sample.db")))

# ─── Logging ─────────────────────────────────────────────────────────────────
# Log to a file so tool calls are diagnosable without attaching a debugger.
# First step when a tool stops working: tail -f tool_debug.log

logging.basicConfig(
    filename=str(BASE_DIR / "tool_debug.log"),
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
log = logging.getLogger(__name__)

# ─── Server ──────────────────────────────────────────────────────────────────

mcp = FastMCP("sqlite-tools")


@mcp.tool()
def query_db(sql: str) -> str:
    """Run a read-only SELECT query on the SQLite sample database.

    Returns rows as a JSON array of objects: [{"col": val, ...}, ...]
    Returns {"error": "message"} on any failure.

    Only SELECT, WITH (CTEs), EXPLAIN, and PRAGMA are allowed.
    Write operations (INSERT, UPDATE, DELETE, DROP) are blocked at the
    database level — the connection is opened in read-only mode.
    """
    log.debug("query_db called | sql=%r | db=%s", sql, DB_PATH)
    result = _query_db(sql, DB_PATH)
    log.debug("query_db result | length=%d | preview=%s", len(result), result[:120])
    return result


@mcp.tool()
def read_file(path: str) -> str:
    """Read a file from the data/ directory.

    Returns the file content as a plain string.
    Returns {"error": "message"} on any failure.

    Only files inside the data/ directory are accessible.
    Files larger than 50 KB or non-UTF-8 files are rejected.
    """
    log.debug("read_file called | path=%r | allowed_dir=%s", path, DATA_DIR)
    result = _read_file(path, DATA_DIR)
    log.debug("read_file result | length=%d", len(result))
    return result


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("sqlite-tools MCP server starting | db=%s | data_dir=%s", DB_PATH, DATA_DIR)
    mcp.run(transport="stdio")
