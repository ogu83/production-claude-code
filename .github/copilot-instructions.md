# Copilot Instructions — production-claude-code

This repo is the companion codebase for the "Claude Code in Production" YouTube series.
Each `ep<N>-*` directory is a standalone teaching unit. There are no cross-episode
runtime dependencies — episodes can be read and modified independently.

## Repository structure

```
ep1-claude-md-architecture/   CLAUDE.md templates + token budget analyser
ep2-hooks/                    Hook scripts (bash + Python) for Claude Code settings.json
ep3-mcp-server/               FastMCP server with two tools, pytest suite
ep4-context-management/       State templates, PreCompact hook, budget simulator
```

Only `ep3-mcp-server/` has a `requirements.txt` and a test suite. The other episodes
contain standalone scripts or configuration files.

## Running tests (ep3 only)

```bash
cd ep3-mcp-server
pip install -r requirements.txt
python create_db.py          # bootstrap data/sample.db before first run

pytest test_server.py -v                    # all 20 tests
pytest test_server.py -v -k "query"         # query tool tests only
pytest test_server.py -v -k "file"          # file tool tests only
```

Tests import tool functions directly — no MCP server process, no API key required.

## Running the stdlib-only scripts

```bash
# ep1 — token budget analyser
python ep1-claude-md-architecture/validate_claude_md.py path/to/CLAUDE.md
python ep1-claude-md-architecture/validate_claude_md.py path/to/CLAUDE.md --turns 50 --target-tokens 100

# ep4 — session budget simulator
python ep4-context-management/context_budget.py --claude-md path/to/CLAUDE.md
python ep4-context-management/context_budget.py --claude-md path/to/CLAUDE.md --turns 200 --avg-turn-tokens 1500
```

Both scripts are stdlib-only — no `pip install` needed.

## Architecture: the four-layer stack

The episodes form a layered system designed to work together:

| Layer | Episode | Role |
|---|---|---|
| CLAUDE.md | ep1 | Context injection — what Claude thinks about each turn |
| Hooks | ep2 | Enforcement — gates at tool boundaries, state persistence |
| MCP server | ep3 | Capability — tools Claude can call to read data |
| State files | ep4 | Compaction survival — `task_state.md` persists across context resets |

Each layer does one job. Understanding the series means understanding which problems
belong to which layer.

## Key conventions

### Python files
- `from __future__ import annotations` on every file (Python 3.8 compatibility).
- Tool functions **never raise**. All failure paths return a JSON error string:
  `json.dumps({"error": "message"})`. This applies to every function called by an MCP tool.
- Token estimate throughout: `chars / 4` (stdlib, no tiktoken dependency).
- Path resolution always uses `Path(__file__).parent` as the base, never `os.getcwd()`.

### MCP tool design (ep3)
- `sqlite3.connect(f"file:{path}?mode=ro", uri=True)` — read-only enforcement at the OS level.
  Do not use application-layer SELECT checks alone; a WITH...DELETE CTE bypasses them.
- Path bounding: `candidate.relative_to(allowed_dir)` inside a `try/except ValueError`.
  Do not use `str.startswith()` — sibling paths like `/data_evil/` pass a `/data` prefix check.
- MCP tool docstrings are the model's interface. Write them for Claude, not for humans:
  describe what it does, what it returns, and what it rejects.

### Hook scripts (ep2)
- **PreToolUse / PostToolUse**: read tool info from **stdin** as JSON.
- **Notification hooks**: read event type from `$CLAUDE_NOTIFICATION_TYPE` env var — never from stdin. Reading stdin in a Notification hook hangs silently.
- Every permissive bash path ends with explicit `exit 0`. The last `grep` in a loop exits 1
  on no-match, which Claude Code treats as an error.
- Exit codes: `0` = allow, `2` = block with message shown to user.
- Hook wiring format (flat array in `.claude/settings.json`):
  ```json
  { "event": "PreToolUse", "matcher": "Bash", "command": "/abs/path/script.sh", "timeout": 10 }
  ```

### Templates (ep4)
- Template files use `<!-- HTML comment blocks -->` for maintainer instructions that Claude
  should remove on first use. Keep embedded instructions minimal — they become context cost.
- `task_state.md` = live intra-session state, updated by Claude after every significant step.
- `session_handoff.md` = deliberate end-of-session summary written once at session close.
  Never conflate the two; they serve different audiences (compaction vs. next session).

### What belongs where
- Enforceable constraints → hooks, not CLAUDE.md prose.
- Module-specific Claude instructions → sub-directory CLAUDE.md, not root CLAUDE.md.
- Anything that must survive compaction → a file on disk, not the conversation.
