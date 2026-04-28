# Daily Notes — context layer

## Structural

This directory contains daily log entries in `YYYY-MM-DD.md` format.

Entry structure:
```
## Focus
[What today's work is about]

## Log
[Timestamped entries as work happens]

## Carry-over
[Tasks not completed — copy to tomorrow's note]
```

Current active date range: review `ls daily-notes/` for the latest entry.

---

## Reference

### To link today's note to a project:
1. Add `[[projects/project-name]]` in the Focus section
2. Add a reciprocal link in `projects/project-name.md` under ## Recent activity

### To find a topic across daily notes:
Use: `grep -r "topic keyword" daily-notes/`

---

<!-- ────────────────────────────────────────────────────────────── -->
<!-- This sub-directory CLAUDE.md adds to the vault root CLAUDE.md. -->
<!-- It only fires when Claude is working inside daily-notes/.       -->
<!-- It does not repeat the vault content map — that is already     -->
<!-- available from the parent CLAUDE.md.                            -->
<!-- ────────────────────────────────────────────────────────────── -->
