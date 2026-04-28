# Claude Code in Production

> **Claude Code in Production** — A YouTube series covering the configuration layer that separates someone who *uses* Claude Code from someone who *runs it in production*.

This repo contains the working files for each episode: CLAUDE.md templates, hook scripts, settings examples, and MCP server code. Not toy demos — take these files and use them directly.

---

## Episodes

| Episode | Topic | Branch | Status |
|---|---|---|---|
| 1 | [CLAUDE.md Architecture](ep1-claude-md-architecture/README.md) | `ep1-claude-md-architecture` | ✅ Published |
| 2 | [Hooks: Turning Text Rules into Enforced Behavior](ep2-hooks/README.md) | `ep2-hooks` | ✅ Published |
| 3 | [MCP Servers: Build One, Wire It In, Make It Reliable](ep3-mcp-server/README.md) | `ep3-mcp-server` | ✅ Published |
| 4 | Context Management: Token Budgets, Compaction, Sessions That Don't Forget | `ep4-context-management` | coming |

---

## Episode 1 — CLAUDE.md Architecture

**Branch:** `ep1-claude-md-architecture`

> "Most CLAUDE.md files are a list of wishes. 'Always do X. Never do Y.' And then Claude does X when it feels like it. Here is why — and how to write CLAUDE.md files that actually work."

| Deliverable | What it is |
|---|---|
| `templates/project.CLAUDE.md` | Fill-in-the-blank template for any code project |
| `templates/global.CLAUDE.md` | Template for `~/.claude/CLAUDE.md` — cross-project defaults |
| `examples/vault-project/CLAUDE.md` | Concrete example: Obsidian-style knowledge vault |
| `examples/vault-project/daily-notes/CLAUDE.md` | Sub-directory layer example: daily notes context |
| `examples/api-project/CLAUDE.md` | Concrete example: FastAPI backend service |
| `examples/api-project/app/CLAUDE.md` | Sub-directory layer example: API application layer context |
| `validate_claude_md.py` | Token budget analyser — shows the cost of your CLAUDE.md per session |

[→ Episode 1 README](ep1-claude-md-architecture/README.md)

---

## Episode 2 — Hooks: Turning Text Rules into Enforced Behavior

**Branch:** `ep2-hooks`

> "Text rules get ignored. Hooks do not get ignored. Here is how to move the things that actually matter out of prose and into code that runs every time."

| Deliverable | What it is |
|---|---|
| `guards/destructive_command_guard.sh` | PreToolUse: blocks `rm -rf`, `DROP TABLE`, `git push --force`, and more |
| `guards/select_guard.py` | PreToolUse: blocks any non-SELECT SQL query |
| `state/compaction_save.sh` | Notification:PreCompact: timestamps `task_state.md` before compaction |
| `state/compaction_restore.sh` | Standalone: prints `task_state.md` at session start |
| `state/task_state.md.template` | Template for Claude to maintain task state mid-session |
| `gates/test_gate.sh` | PostToolUse: runs pytest after `git commit`, stops agent on failure |
| `debug/hook_debug.sh` | Debug utility: logs all hook inputs to `/tmp/hook_debug.log` |
| `settings.json.example` | How to wire all hooks into `.claude/settings.json` |

[→ Episode 2 README](ep2-hooks/README.md)

---

## Episode 3 — MCP Servers: Build One, Wire It In, Make It Reliable

**Branch:** `ep3-mcp-server`

> "An MCP server is how you give Claude Code a hand. Instead of copy-pasting context into the chat every session, you write a tool — and Claude calls it when it needs it."

| Deliverable | What it is |
|---|---|
| `server.py` | FastMCP entry point — two tools, env-configured DB path, debug logging |
| `create_db.py` | Bootstrap: creates `data/sample.db` (17 products, 30 orders) |
| `tools/query_tool.py` | `query_db`: SELECT-only enforcement via prefix check + `sqlite3 mode=ro` |
| `tools/read_file_tool.py` | `read_file`: path bounding via `pathlib.resolve()` + `is_relative_to()` |
| `.claude.json.example` | `mcpServers` wiring block for `.claude.json` |
| `test_server.py` | 20 tests covering both tools — no API key or MCP session needed |

[→ Episode 3 README](ep3-mcp-server/README.md)

---

## Episode 4 — Context Management *(coming)*

**Branch:** `ep4-context-management`

Two reusable templates: `task_state.md` and `session_handoff.md`. Survive compaction by design.

---

**GitHub:** [github.com/ogu83/production-claude-code](https://github.com/ogu83/production-claude-code)
