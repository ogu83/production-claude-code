# Episode 3 — MCP Servers: Build One, Wire It In, Make It Reliable

> "An MCP server is how you give Claude Code a hand. Instead of copy-pasting context into the chat every session, you write a tool — and Claude calls it when it needs it."

---

## The three-layer model

| Layer | Mechanism | Role |
|---|---|---|
| **CLAUDE.md** | Context injection | Tells Claude what to think about. Influences decisions. Probabilistic. |
| **Hooks** | Shell scripts at tool boundaries | Gates existing tools. Runs before/after tool calls. Deterministic. |
| **MCP Server** | Out-of-process capability | Adds new tools. Claude calls them; server runs code. |

Build an MCP server when Claude needs to do something it currently cannot do at all —
call an API, query a database, read a bounded set of files. Build hooks when you need to
control what Claude already does.

---

## The three MCP primitives

| Primitive | What it is | When to use |
|---|---|---|
| **Tools** | Callable functions — Claude sends typed inputs, server returns result | 90% of production use cases |
| **Resources** | Readable URIs — Claude reads a URI, server returns content | Static/slow-changing data: schema files, lookup tables |
| **Prompts** | Preconfigured message templates | Rarely needed in Claude Code production setups |

Tools are the primary primitive. If you are not sure which to use, use a tool.

---

## This server: sqlite-tools

Two tools that demonstrate the three key design principles — guard at the boundary,
explicit error returns, structured output.

### `query_db(sql)` — SELECT-only SQLite query

Returns rows as a JSON array: `[{"col": val, ...}, ...]`

Enforcement at two levels:
1. **Prefix check** — first SQL token must be `SELECT`, `WITH`, `EXPLAIN`, or `PRAGMA`.
   Non-SELECT queries get a clear error message before the DB is touched.
2. **Read-only DB connection** — `sqlite3.connect(uri, uri=True)` with `mode=ro` opens
   the database at the OS level in read-only mode. A `WITH ... DELETE` CTE that slips
   past the prefix check fails at the DB level. The model cannot override Python code.

### `read_file(path)` — bounded file read

Returns file content as a plain string.

Enforcement:
- **Path bounding** — `Path.resolve()` + `is_relative_to()` — collapses `../` traversal
  before the check, and correctly rejects sibling paths (e.g. `/data_evil/` is not
  inside `/data/`). String `startswith()` is not safe for this check.
- **Size limit** — 50 KB cap prevents accidental context blowups.
- **Encoding guard** — rejects binary files with a clear error.

---

## Setup

```bash
cd ep3-mcp-server
pip install -r requirements.txt

# Bootstrap the sample database (run once)
python create_db.py
```

This creates `data/sample.db` with:
- `products` — 17 products across 4 categories (Electronics, Office, Books, Wellness)
- `orders` — 30 orders (pending / shipped / delivered / returned)

---

## Test

```bash
# No API key, no Claude Code session required
pytest test_server.py -v
```

Tests cover: SELECT queries, WITH CTEs, blocked writes, path traversal, sibling dir
bypass, missing files, large files, binary files.

---

## Wire into Claude Code

1. Copy `.claude.json.example` to `.claude.json` in your project root.
2. Replace `/ABSOLUTE/PATH/TO/` with real paths. Use forward slashes even on Windows.
3. Restart Claude Code — MCP server changes take effect in the next session.

```json
{
  "mcpServers": {
    "sqlite-tools": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/ep3-mcp-server",
      "env": {
        "DB_PATH": "/absolute/path/to/ep3-mcp-server/data/sample.db"
      }
    }
  }
}
```

Field reference:

| Field | Notes |
|---|---|
| `command` | The Python executable. Use your venv's full path if using a dedicated environment. |
| `args` | Arguments to the command. Path to `server.py`. |
| `cwd` | Working directory for the server process. Relative paths in tool code resolve from here. |
| `env` | Environment variables the server process receives. Set DB paths and API keys here. |

**Windows path note:** Backslashes in paths get mangled when registered via the `claude mcp add` CLI.
Fix: register via CLI first, then edit `.claude.json` directly and use forward slashes.

---

## Diagnosing silent failures

When an MCP tool stops working, work through this checklist:

1. **Server didn't start** — Import error, missing dependency, or syntax error at startup.
   Claude Code continues without the server and does not surface the startup error.
   Fix: run `python server.py` in a terminal before the session and confirm it starts cleanly.

2. **Tool not being offered** — Bad decorator, missing docstring, or failed registration.
   Claude doesn't know the tool exists.
   Fix: ask Claude "what tools do you have?" If the tool is missing, check the session
   startup logs for MCP server errors.

3. **Tool called but output silently discarded** — Tool returns a JSON error object.
   Claude receives it but may not surface it — the session continues as if it succeeded.
   Fix: check `tool_debug.log` (created automatically in the ep3-mcp-server directory).
   Every call and return value is logged at DEBUG level.

4. **Environment and path mismatch** — The server process does not inherit your terminal
   environment. Relative paths resolve from `cwd`, not your project root.
   Fix: set all paths and env vars in the `env` field of `.claude.json`. Use `cwd` to
   anchor relative paths.

---

## Logging

`tool_debug.log` is written automatically by `server.py` whenever it starts and on every
tool call. It is the first place to look when something is not working.

```bash
# Follow log in real time while Claude is running
tail -f ep3-mcp-server/tool_debug.log
```

Add to `.gitignore`: `tool_debug.log`

---

## Files in this episode

```
ep3-mcp-server/
  server.py                # FastMCP entry point, env-configured DB path, logging
  create_db.py             # bootstrap: creates data/sample.db
  tools/
    __init__.py
    query_tool.py          # SELECT-only query: prefix check + mode=ro enforcement
    read_file_tool.py      # path-bounded read: resolve() + is_relative_to()
  data/
    README.md              # explains data/ — run create_db.py before using
    sample.db              # (generated — not committed)
  .claude.json.example     # mcpServers block for wiring into Claude Code
  test_server.py           # 20 tests for both tools, no MCP session required
  requirements.txt
  README.md                # this file
```

---

## Key takeaways

1. **MCP adds capability. Hooks gate it.** Build MCP servers when Claude needs to do
   something new. Build hooks when you need to control what Claude already does.

2. **Tools are the primary primitive.** Resources and Prompts exist. For production
   Claude Code setups, you need tools ninety percent of the time.

3. **Enforce at the tool boundary.** SELECT guards, path bounds, and input validation
   belong inside the tool function. The model cannot override Python code.

4. **Log everything in development.** Silent failure is the hardest MCP problem to debug.
   Log calls and returns from day one. `tool_debug.log` is there for this reason.

---

**Repo:** github.com/ogu83/production-claude-code · branch ep3-mcp-server

**Previous:** Episode 2 -> Hooks: Turning Text Rules into Enforced Behavior
**Next:** Episode 4 -> Context Management: Token Budgets, Compaction, and Sessions That Don't Forget
