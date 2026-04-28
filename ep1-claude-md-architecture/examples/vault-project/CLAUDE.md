# Knowledge Vault

## What this vault is

Personal knowledge management system for research notes, project documentation, and
weekly reviews. Managed via Claude Code — Claude reads, links, and synthesises notes
on request.

## Content map

| Directory / File           | Purpose                                         |
|----------------------------|-------------------------------------------------|
| `daily-notes/`             | Daily log entries — YYYY-MM-DD.md format        |
| `projects/`                | One subdirectory per active project             |
| `research/`                | Topic deep-dives, reading notes, summaries      |
| `templates/`               | Note templates (daily, weekly, project kickoff) |
| `index.md`                 | Master topic index — updated weekly             |
| `_attachments/`            | Images and PDFs linked from notes               |

Note format: Markdown. Frontmatter: `date`, `tags`, `status` (active/archived).

---

## Structural

<!-- ↑ Content map above. Always useful — tells Claude where things live. -->

---

## Reference

### To create a daily note:
1. Copy `templates/daily.md`
2. Rename to `daily-notes/YYYY-MM-DD.md`
3. Fill in: date, yesterday's carry-over tasks, today's focus
4. Link to any relevant project files

### To summarise a research topic:
1. Gather all notes tagged with the topic from `research/`
2. Identify the three most important insights
3. Write a 200-word synthesis to `research/[topic]-summary.md`
4. Update `index.md` with the new summary link

### To do a weekly review:
1. Read all daily notes from the past 7 days
2. Identify completed tasks, open threads, and recurring themes
3. Write summary to `daily-notes/YYYY-WW-weekly.md`

---

## Behavioral

Keep internal links relative (e.g., `../projects/api-service.md` not absolute paths).
Preserve existing frontmatter when editing notes — do not remove `date` or `status` fields.
