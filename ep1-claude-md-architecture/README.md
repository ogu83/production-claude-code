# Episode 1 — CLAUDE.md Architecture

> How Claude Code Actually Reads Your Instructions

---

## The problem

Most CLAUDE.md files look like this:

```
Always use environment variables for secrets.
Never modify production data without confirmation.
Always write tests before implementing features.
Never use git force push.
```

And then Claude ignores them — not always, but often enough to cause real damage. This is not
a Claude bug. It is a misunderstanding of what CLAUDE.md actually is.

---

## What CLAUDE.md actually is

CLAUDE.md is part of the prompt. It is loaded and injected into the context window on
**every single turn** — not once at startup, not once per session. Every time you send a
message, every CLAUDE.md file in the hierarchy is re-read and prepended to the context.

This has two consequences:

1. Every byte of CLAUDE.md costs token budget on every turn.
2. CLAUDE.md competes with conversation history, file contents, and tool results for context
   space. In long sessions, that competition intensifies — and prose behavioral rules are
   usually the first thing that gets deprioritised.

---

## Three categories of content

| Category | Reliability | What belongs here |
|---|---|---|
| **Structural** | Always relevant | File map, folder layout, stack description, content overview |
| **Reference** | Good when structured | Numbered workflows, deployment steps, how-to procedures |
| **Behavioral** | Probabilistic | Short prose rules — low blast-radius only |

**Structural content earns its place.** A table mapping filenames to their purpose is always
relevant — it does not matter what the current task is, that context helps.

**Reference content works when structured.** A numbered list of "how to add an endpoint" is
consulted when Claude is about to add an endpoint. Structure (numbered steps, explicit
headings) makes this reliable.

**Behavioral content is probabilistic.** Prose rules compete for context. In a short session
on a focused task, `Always use environment variables` will likely be respected. In a long
refactor session, it may not be. **The rule of thumb: if a single violation is unacceptable,
do not use CLAUDE.md. Use a hook.**

---

## The hierarchy

```
~/.claude/CLAUDE.md          <- Global: personal preferences, cross-project defaults
         |
project/CLAUDE.md            <- Project: content map, stack, workflows
         |
project/subdir/CLAUDE.md     <- Sub-directory: domain-specific context
```

All applicable files are concatenated and injected together. This is **additive** — there is
no override mechanism. A sub-directory CLAUDE.md adds to the project CLAUDE.md, it does not
replace it.

**Practical consequence:** A focused 20-line sub-directory CLAUDE.md for `frontend/` beats
a 100-line project CLAUDE.md that mixes frontend, backend, and infrastructure concerns.
Split by concern.

---

## CLAUDE.md vs. hooks

The decision is the blast-radius test:

> **What is the cost of a single violation?**

| Decision rule | Use |
|---|---|
| Violation is annoying but recoverable | CLAUDE.md (behavioral section) |
| Violation causes data loss, security incident, or broken CI | Hook |

Examples in CLAUDE.md:
- Code style preferences
- Naming conventions
- Documentation habits

Examples that belong in a hook:
- No destructive shell commands without confirmation
- No committing secrets
- No writing to production
- Save task state before compaction
- Run linter after every code edit

Episode 2 covers hooks in detail.

---

## Token budget

Every CLAUDE.md file is loaded on every turn. The cost is not one-time — it accumulates.

```
50-turn session x 480 tokens (verbose CLAUDE.md)    = 24,000 tokens on instruction injection
50-turn session x  95 tokens (disciplined CLAUDE.md) =  4,750 tokens on instruction injection
                                                        ─────────────────────────────────────
                                                         19,250 tokens freed for actual work
```

The `validate_claude_md.py` script in this directory calculates this for any CLAUDE.md file.

---

## Files in this episode

```
ep1-claude-md-architecture/
  templates/
    project.CLAUDE.md        # fill-in-the-blank template for any code project
    global.CLAUDE.md         # template for ~/.claude/CLAUDE.md
  examples/
    vault-project/
      CLAUDE.md              # Obsidian-style knowledge vault
      daily-notes/
        CLAUDE.md            # sub-directory layer: daily notes context
      README.md
    api-project/
      CLAUDE.md              # FastAPI backend service
      app/
        CLAUDE.md            # sub-directory layer: API application layer
      README.md
  validate_claude_md.py      # token budget analyser
  README.md                  # this file
```

---

## Key takeaways

1. **CLAUDE.md is part of the prompt** — loaded every turn, competes for context. Design it
   like a briefing document, not a rulebook.

2. **Three categories** — Structural (reliable), Reference (good when structured), Behavioral
   (probabilistic, low blast-radius only). Most CLAUDE.md files over-invest in behavioral
   and under-invest in structural.

3. **Hard constraints belong in hooks** — if a single violation is unacceptable, CLAUDE.md
   is the wrong place for it.

4. **Use the hierarchy** — global for personal defaults, project for content map and
   workflows, sub-directory for domain context. Split by concern, not by length.

---

**Repo:** github.com/ogu83/production-claude-code · branch ep1-claude-md-architecture

**Next:** Episode 2 -> Hooks: Turning Text Rules into Enforced Behavior
