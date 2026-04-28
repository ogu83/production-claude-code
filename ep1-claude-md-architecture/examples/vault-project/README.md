# Vault Project Example

This example shows a CLAUDE.md setup for a personal knowledge vault — notes, research,
and project documentation managed via Claude Code.

## File tree

```
vault-project/
  CLAUDE.md                    # project-level: content map + workflows
  daily-notes/
    CLAUDE.md                  # sub-directory layer: daily-note format + linking rules
    2025-01-15.md              # (not included — your actual notes go here)
  projects/
    (your project notes)
  research/
    (your research notes)
  templates/
    (your note templates)
  index.md                     # (not included — your master topic index)
```

## What this demonstrates

**CLAUDE.md (project root):**
- Structural section: content map table showing every directory and its purpose
- Reference section: three numbered workflows (create daily note, summarise topic, weekly review)
- Behavioral section: two short rules about link format and frontmatter preservation

**daily-notes/CLAUDE.md (sub-directory):**
- Structural section: entry format for daily notes
- Reference section: how to link notes to projects and search across notes
- No behavioral rules — the parent's rules apply here too
- No redundant content — does not repeat the vault content map

## Key teaching point

When working inside `daily-notes/`, Claude sees **both** the vault root CLAUDE.md and the
`daily-notes/CLAUDE.md`. The sub-directory file does not replace the parent — it adds to it.
This means the daily-notes context is available without polluting the top-level file.

Without the sub-directory split, you would either:
- Duplicate the daily-note format in the root CLAUDE.md (wastes tokens on every turn, even
  when Claude is not working in daily-notes)
- Or omit it (Claude does not know the entry format)

The hierarchy solves this.
