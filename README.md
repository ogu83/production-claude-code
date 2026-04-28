# Claude Code in Production

> **Claude Code in Production** — A YouTube series covering the configuration layer that separates someone who *uses* Claude Code from someone who *runs it in production*.

This repo contains the working files for each episode: CLAUDE.md templates, hook scripts, settings examples, and MCP server code. Not toy demos — take these files and use them directly.

---

## Episodes

| Episode | Topic | Branch | Status |
|---|---|---|---|
| 1 | [CLAUDE.md Architecture](ep1-claude-md-architecture/README.md) | `ep1-claude-md-architecture` | ✅ Published |
| 2 | Hooks: Turning Text Rules into Enforced Behavior | `ep2-hooks` | coming |
| 3 | MCP Servers: Build One, Wire It In, Make It Reliable | `ep3-mcp-server` | coming |
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

## Episode 2 — Hooks *(coming)*

**Branch:** `ep2-hooks`

Three working hooks: destructive command guard, compaction state save/restore, test gate before commit.

---

## Episode 3 — MCP Servers *(coming)*

**Branch:** `ep3-mcp-server`

Minimal Python MCP server with a SQLite query tool and a file-read tool, wired into Claude Code.

---

## Episode 4 — Context Management *(coming)*

**Branch:** `ep4-context-management`

Two reusable templates: `task_state.md` and `session_handoff.md`. Survive compaction by design.

---

**GitHub:** [github.com/ogu83/production-claude-code](https://github.com/ogu83/production-claude-code)
