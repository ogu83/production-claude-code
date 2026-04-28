# API Project Example

This example shows a CLAUDE.md setup for a FastAPI backend service — a concrete instantiation
of the `templates/project.CLAUDE.md` template.

## File tree

```
api-project/
  CLAUDE.md                    # project-level: content map + workflows + behavioral
  app/
    CLAUDE.md                  # sub-directory layer: module responsibilities + error taxonomy
    routes.py                  # (not included — illustrative)
    models.py
    client.py
    validators.py
  tests/
    test_routes.py             # (not included — illustrative)
    test_models.py
  main.py
```

## What this demonstrates

**CLAUDE.md (project root):**
- Structural section: content map table (8 entries, file + purpose)
- Reference section: four numbered workflows (add enrichment field, run locally, run tests,
  add endpoint)
- Behavioral section: one short rule — 2 lines

**app/CLAUDE.md (sub-directory):**
- Structural section: module-level responsibility table + error taxonomy
- Reference section: how to add a field validator, Claude client usage pattern
- No behavioral rules — the project root's rule applies here too
- No redundant content — does not repeat the top-level content map or workflows

## Key teaching point

The `app/CLAUDE.md` adds **module-level detail** that is only relevant when Claude is editing
code inside `app/`. The error taxonomy (422/502/503) is exactly the kind of structural
reference that earns its token cost — without it, Claude would have to infer the error
handling pattern from reading the code.

The sub-directory split keeps the project root CLAUDE.md clean: 35 lines covering the whole
project, rather than 60+ lines mixing project-level and module-level concerns.
