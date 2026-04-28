# Episode 2 — Hooks: Turning Text Rules into Enforced Behavior

> "Text rules get ignored. Hooks do not get ignored."

---

## The problem

CLAUDE.md behavioral rules are probabilistic. `Never run rm -rf without checking first` is
followed most of the time. In a long refactor session under pressure, it may not be. The
problem is not Claude — it is where the constraint lives. A prose rule lives in the reasoning
layer. A hook lives at the execution layer — the shell — where it runs every time, without
exception.

**The boundary:** If a single violation is unacceptable, the constraint belongs in a hook,
not in CLAUDE.md.

---

## The four hook events

| Event | When it fires | stdin / env vars | Can block? |
|---|---|---|---|
| `PreToolUse` | Before a tool runs | **stdin** (JSON) | Yes — exit 2 |
| `PostToolUse` | After a tool runs | **stdin** (JSON) | Exit 2 stops agent loop; tool already ran |
| `Notification` | Session lifecycle events (PreCompact, etc.) | **env vars** | No blocking |
| `Stop` | End of a turn | **env vars** | Rarely used for enforcement |

### The single detail that separates working hooks from silent failures

**PreToolUse and PostToolUse** pass tool information via **stdin** as a JSON object:
```json
{
  "tool_name": "Bash",
  "tool_input": { "command": "rm -rf /tmp/build" }
}
```

**Notification hooks** pass data via **environment variables**:
```bash
CLAUDE_NOTIFICATION_TYPE=PreCompact
CLAUDE_NOTIFICATION_DATA=...
```

Reading stdin in a Notification hook will hang or read nothing and exit 0 silently.
This is the most common reason community hooks do not work.

---

## Exit codes

| Exit code | Meaning |
|---|---|
| `0` | Allow — tool runs normally, agent continues |
| `2` | Block — stdout message is shown to the user, agent loop stops |
| other | Unexpected error — treated as allow |

Always end every permissive code path with an explicit `exit 0`. In bash, the exit code
of the script is the exit code of the last command run — `grep` with no match exits `1`,
not `0`. A missing `exit 0` is a silent failure.

---

## Hooks in this episode

### `guards/destructive_command_guard.sh` — PreToolUse
Intercepts every Bash tool call and blocks commands that match a list of destructive
patterns before execution:

```
rm -rf, rm -r, git reset --hard, git push --force, git push --force-with-lease,
DROP TABLE, DROP DATABASE, TRUNCATE, DELETE FROM, mkfs, dd if=
```

Patterns are case-insensitive. If matched, the hook prints a clear message and exits 2 —
the command never runs.

### `guards/select_guard.py` — PreToolUse
Intercepts SQL tool calls and blocks any query that is not read-only. Accepts `SELECT`,
`WITH` (CTEs), `EXPLAIN`, `SHOW`, and `DESCRIBE`. Rejects everything else.

Strips leading SQL comments and whitespace before checking, so `/* comment */ DELETE FROM`
is caught correctly. Configure the `matcher` in `settings.json` to target your specific
SQL tool name.

### `state/compaction_save.sh` — Notification:PreCompact
Fires just before Claude Code summarises the context window. Appends a timestamped
compaction marker to `task_state.md`. Reads from `$CLAUDE_NOTIFICATION_TYPE` (env var),
not stdin.

This hook does the timestamping. Claude writes the actual task content during the session.
Division of responsibility: the agent maintains state, the hook records when it was last
checkpointed.

### `state/compaction_restore.sh` — standalone script
Not a hook. Run this at the start of a new session to read `task_state.md` and resume.
Add to your CLAUDE.md: `"At the start of every session, run: bash ep2-hooks/state/compaction_restore.sh"`.

### `state/task_state.md.template`
The template Claude uses to maintain task state during a session. Copy it to your project
root and instruct Claude to update it after every significant step.

### `gates/test_gate.sh` — PostToolUse
Fires after a Bash `git commit` command. Runs `pytest tests/ -q` and exits 2 if tests are
failing.

**Important:** PostToolUse fires after the tool has run. The commit already exists when
this hook fires. Exit 2 cannot undo it — it stops the agent loop and surfaces the failure
so Claude does not continue building on a broken commit. It is an emergency brake, not an
undo.

For a true gate (prevents the commit entirely), move this hook to `PreToolUse`. The
trade-off: `PreToolUse` will also block WIP commits. PostToolUse is the safer default for
most development workflows.

### `debug/hook_debug.sh` — debug utility
Logs all hook inputs to `/tmp/hook_debug.log`. Use this as the first step when a hook is
not firing or doing nothing. Wire it to the event you are debugging with `"matcher": "*"`,
trigger the event, then read the log.

---

## Wiring hooks: .claude/settings.json

This file lives at `.claude/settings.json` in your project root. Changes take effect
immediately — no session restart needed.

```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": "Bash",
      "command": "/absolute/path/to/ep2-hooks/guards/destructive_command_guard.sh",
      "timeout": 10
    },
    {
      "event": "PreToolUse",
      "matcher": "execute_sql",
      "command": "/absolute/path/to/ep2-hooks/guards/select_guard.py",
      "timeout": 10
    },
    {
      "event": "Notification",
      "matcher": "PreCompact",
      "command": "/absolute/path/to/ep2-hooks/state/compaction_save.sh",
      "timeout": 10
    },
    {
      "event": "PostToolUse",
      "matcher": "Bash",
      "command": "/absolute/path/to/ep2-hooks/gates/test_gate.sh",
      "timeout": 60
    }
  ]
}
```

Field reference:

| Field | Notes |
|---|---|
| `event` | `PreToolUse`, `PostToolUse`, `Notification`, `Stop` |
| `matcher` | Tool name or notification type. `*` matches all. |
| `command` | **Use absolute paths.** Relative paths break when the project moves. |
| `timeout` | Seconds before the hook is killed. Default 10. Raise for slow operations (test suites). |

---

## Diagnosing silent failures

When a hook does nothing, work through this checklist:

1. **Hook is not firing at all** — Check the event name spelling in `settings.json`. A typo
   means the hook never matches. Wire `hook_debug.sh` with `"matcher": "*"` to confirm the
   hook fires at all.

2. **Reading stdin in a Notification hook** — Notification events pass data via env vars.
   stdin is empty. The script reads nothing and exits 0 without doing anything. Use
   `$CLAUDE_NOTIFICATION_TYPE` instead.

3. **Missing explicit `exit 0`** — In bash, the exit code of the script is the exit code
   of the last command run. If the last command is `grep` with no match, the script exits 1.
   Exit 1 is treated as an unexpected error and Claude Code allows the operation anyway.
   Add `exit 0` as the final line of every permissive code path.

4. **Hook timeout exceeded** — Hooks are killed after `timeout` seconds and treated as
   errors (allowed). If your test suite takes 45 seconds and the timeout is 10, the gate
   never actually gates. Raise the timeout to match your test suite.

---

## Files in this episode

```
ep2-hooks/
  guards/
    destructive_command_guard.sh   # PreToolUse: blocks rm -rf, DROP TABLE, etc.
    select_guard.py                # PreToolUse: blocks non-SELECT SQL
  state/
    compaction_save.sh             # Notification:PreCompact: timestamps task_state.md
    compaction_restore.sh          # standalone: prints task_state.md on session start
    task_state.md.template         # template for Claude to maintain task state
  gates/
    test_gate.sh                   # PostToolUse: runs pytest after git commit
  debug/
    hook_debug.sh                  # debug utility: logs all hook inputs
  settings.json.example            # wiring all hooks into .claude/settings.json
  README.md                        # this file
```

---

## Key takeaways

1. **Hooks enforce, CLAUDE.md guides.** Hard constraints belong at the shell level.
   CLAUDE.md is for context and guidance, not enforcement.

2. **Know your event type.** PreToolUse for blocking before execution. PostToolUse for
   reacting after. Notification:PreCompact for state preservation before compaction.

3. **stdin for PreToolUse / PostToolUse — env vars for Notification.** This single
   detail separates working hooks from silent failures.

4. **State belongs in files, not conversations.** Claude writes `task_state.md` during
   the session. The PreCompact hook timestamps it. New sessions read the file and resume.

---

**Repo:** github.com/ogu83/production-claude-code · branch ep2-hooks

**Previous:** Episode 1 -> CLAUDE.md Architecture
**Next:** Episode 3 -> MCP Servers: Build One, Wire It In, Make It Reliable
