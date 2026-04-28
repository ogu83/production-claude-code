# Episode 4 — Context Management: Token Budgets, Compaction, and Sessions That Don't Forget

> "Every Claude Code session has a finite context window. At some point it fills up, compaction happens, and the session forgets what it was doing. Here is how to design your setup so that does not matter."

---

## What is in the context window

Every turn in a Claude Code session draws from a shared token budget:

| Component | Token behaviour | Notes |
|---|---|---|
| **Conversation history** | Grows every turn | Every user message, assistant response, tool call |
| **Tool results** | Stays in context | Bash outputs, MCP returns, grep results — until compaction |
| **CLAUDE.md** | Reloaded every turn | Every byte × every turn = recurring cost, not one-time |
| **File reads** | Stays in context | File content after a Read tool call |

**The key insight on CLAUDE.md:** It is not a one-time load. It is reloaded on every turn for the entire session. A 500-token CLAUDE.md across a 200-turn session costs 100,000 tokens — just in CLAUDE.md load cost.

---

## Compaction: what survives and what does not

When context fills up, Claude Code summarises the conversation to free space. The raw messages are replaced by a prose summary.

| What is **lost** | What **survives** |
|---|---|
| Raw conversation history | The compaction summary (prose) |
| Individual tool outputs | CLAUDE.md (reloaded fresh) |
| File content from earlier reads | `task_state.md` — if it was on disk |
| Intermediate reasoning | The next user message |

**The design implication:** If task state exists only in the conversation, compaction will degrade or lose it. Write state to a file. The file survives. The conversation does not.

---

## The two state files

### `task_state.md` — intra-session running log

Updated by Claude after every significant step during a session. Read by the compaction hook before each compaction. Read by the next session if it continues the same task.

**Update trigger:** After every significant step — file modified, test run, decision made.

**Structure:**
- **Current Task** — one or two sentences. What is being built right now.
- **Done** — chronological checklist. One line per step, which file, what outcome.
- **Next Step** — one concrete action. A new session reads this line first.
- **Open Questions** — deferred decisions and noticed-but-not-addressed problems.

See `patterns/task_state.md.template` for the full template with examples.

### `session_handoff.md` — deliberate end-of-session summary

Written when you choose to close a session. Richer and more intentional than `task_state.md`. Read at the start of the next session to pick up exactly where you left off.

**Structure:**
- **Task Completed** — one paragraph describing what was actually built.
- **Files Changed** — every file touched. One line per file.
- **Current State** — snapshot: what works, what does not, what is known. Include regressions.
- **Deferred / Abandoned** — the most important section. Decisions made by not making them.
- **Next Session Start Instructions** — 3–5 numbered steps. First is always: read this file.

See `patterns/session_handoff.md.template` for the full template with examples.

**Difference from `task_state.md`:**

| | `task_state.md` | `session_handoff.md` |
|---|---|---|
| Updated by | Claude, after every step | You (or Claude), at deliberate session end |
| Timing | Continuous, during session | Once, at session close |
| Purpose | Survive compaction mid-session | Transfer context across sessions |
| Audience | The current session after compaction | The next fresh session |

---

## CLAUDE.md token discipline

Every byte of CLAUDE.md is paid for on every turn. The token cost is not per session — it is per turn, multiplied by the session length.

**Before → After example (see `examples/long_session_CLAUDE.md` for the "after"):**

```
Before: 350 lines ≈ 8,750 tokens/turn
After:  180 lines ≈ 4,500 tokens/turn
Savings: 4,250 tokens/turn × 200 turns = 850,000 tokens per long session
```

**What was removed:**

| Removed | Reason |
|---|---|
| Prose behavioral rules ("Always add tests", "Never use magic strings") | Probabilistic. Hook-enforceable rules belong in hooks, not context. |
| Commit checklist ("Before any commit, run tests") | Enforced by `test_gate.sh` hook. Stating it twice wastes tokens. |
| Destructive command warnings | Enforced by `destructive_command_guard.sh` hook. |
| Long onboarding prose | Not relevant to active turns. |

**What was kept:**

| Kept | Reason |
|---|---|
| Directory layout | Structural — always relevant. Saves Claude having to explore. |
| File map (what to look for and where) | Structural — saves downstream Read tool calls. |
| Numbered workflows (run tests, run locally) | Reference — looked up on demand. |
| Session state instruction | Behavioral — short, high-value, establishes the state-file pattern. |

**Three CLAUDE.md disciplines:**
1. **Structural content pays for itself** — a file map prevents Read tool calls that cost more context than the map.
2. **Cut the wishlist** — prose rules are tokens spent on probabilistic behavior. Move enforceable rules to hooks.
3. **Use the hierarchy** — sub-directory CLAUDE.md files load only when relevant. Module-specific instructions belong there.

---

## The PreCompact hook

`examples/state_save_hook.sh` fires on `Notification:PreCompact` — just before Claude Code summarises the context window.

What it does:
1. Checks `$CLAUDE_NOTIFICATION_TYPE == "PreCompact"` (env var, not stdin)
2. Appends a timestamped compaction marker to `task_state.md` (append-only — no section edits)
3. Writes a one-line diagnostic entry to `.claude/compaction_log.txt`

**Critical:** Notification hooks receive data via **environment variables**, not stdin. Reading stdin in a Notification hook hangs silently. This is the most common reason Notification hooks silently do nothing.

Wire in `.claude/settings.json`:
```json
{
  "hooks": [
    {
      "event": "Notification",
      "matcher": "PreCompact",
      "command": "/absolute/path/to/state_save_hook.sh",
      "timeout": 10
    }
  ]
}
```

**EP4 vs EP2:** `ep2-hooks/state/compaction_save.sh` does the same job at a simpler level. Use `ep4-context-management/examples/state_save_hook.sh` as the production version. Do not wire both — they will both append to `task_state.md` on the same event.

---

## When to split sessions deliberately

Do not wait for compaction to force a session transition. Deliberate splits give you control over what the next session knows.

**Split when:**

| Signal | Why |
|---|---|
| Task phase changed | You finished implementing. Now writing tests. A new session starts with full budget and phase-specific context. |
| Context is contaminated | A long debugging session leaves dead-end reasoning in the compaction summary. Starting fresh with only known facts is cleaner. |
| CLAUDE.md changed significantly | New session loads the updated config cleanly from the start. |
| Critical operation ahead | Database migration, deployment, major refactor. Do not enter a critical operation with a depleted budget. |

**Split procedure:**
```
1. Write session_handoff.md          ← capture what matters
2. Commit / save all in-progress work
3. Start a new Claude Code session
4. Begin with: "Read session_handoff.md and pick up from Next Session Start Instructions."
```

---

## `context_budget.py` — session token budget simulator

Estimates token usage across a session and identifies when compaction is likely to trigger.

```bash
# With a CLAUDE.md file
python context_budget.py --claude-md ../ep1-claude-md-architecture/examples/api-project/CLAUDE.md

# Custom session parameters
python context_budget.py \
  --claude-md path/to/CLAUDE.md \
  --turns 200 \
  --avg-turn-tokens 1500 \
  --context-window 200000 \
  --trigger-ratio 0.8
```

Parameters:

| Flag | Default | Meaning |
|---|---|---|
| `--claude-md` | (none) | Path to CLAUDE.md to measure |
| `--turns` | 100 | Estimated session length |
| `--avg-turn-tokens` | 1000 | Avg tokens per turn (user + assistant + tool outputs combined) |
| `--context-window` | 200000 | Context window size in tokens |
| `--trigger-ratio` | 0.8 | Compaction trigger as fraction of context window |

Output: per-turn cost, estimated compaction turn, CLAUDE.md trim savings, session split savings.

**This is a rough simulator.** Actual compaction timing depends on Claude Code's internal sliding-window accounting. Use these numbers for planning and direction, not precision.

---

## The complete session lifecycle

```
Session Start
  └── Read CLAUDE.md (Ep1)
  └── Read task_state.md if exists  ←── Ep4
  └── Read session_handoff.md if exists  ←── Ep4
         │
         ▼
Active Work
  └── Claude writes code, runs tools (Ep3: MCP)
  └── Updates task_state.md after each step  ←── Ep4
  └── Hooks gate destructive operations (Ep2)
         │
         ▼
Context Fills Up
  └── PreCompact hook fires (Ep2 + Ep4)
  └── task_state.md timestamped  ←── Ep4
  └── Claude Code summarises → context reset
  └── Claude reads task_state.md → resumes from Next Step  ←── Ep4
         │
         ▼
Session End (Deliberate)
  └── Write session_handoff.md  ←── Ep4
  └── New session reads handoff → picks up
```

**Four layers, one working setup:** CLAUDE.md (context) + Hooks (enforcement + state) + MCP servers (capability) + State files (compaction survival). Each layer does one job. Together they make production Claude Code reliable.

---

## Files in this episode

```
ep4-context-management/
  patterns/
    task_state.md.template          # intra-session running state
    session_handoff.md.template     # end-of-session summary for next session
  examples/
    long_session_CLAUDE.md          # token-optimised CLAUDE.md (FastAPI project)
    state_save_hook.sh              # Notification:PreCompact hook (append-only)
    settings.json.example           # hook wiring for .claude/settings.json
  context_budget.py                 # token budget simulator (stdlib only)
  README.md                         # this file
```

---

## Key takeaways

1. **Compaction is designed, not a failure.** Design around it. `task_state.md` holds what matters. The PreCompact hook timestamps it. New sessions read the file. Compaction becomes irrelevant.

2. **CLAUDE.md has a token cost per turn — not per session.** Every byte × every turn × session length. Keep structural and reference content. Move prose constraints to hooks.

3. **Deliberate splits beat compaction-forced continuity.** You control what the next session knows. Use `session_handoff.md` when the task phase changes or the budget is depleted.

4. **The four layers stack.** CLAUDE.md (context), Hooks (enforcement + state), MCP servers (capability), State files (compaction survival). Each does one job. Together they make production Claude Code reliable.

---

**Repo:** github.com/ogu83/production-claude-code · branch ep4-context-management

**Previous:** Episode 3 → MCP Servers: Build One, Wire It In, Make It Reliable
