# CLAUDE.md — Web API Project (Token-Optimised)

<!--
  This CLAUDE.md is an example of a token-disciplined configuration.
  Token cost model: tokens(this file) × turns_per_session = recurring context cost.

  Design principles applied here:
    1. Structural content only  — directory layout, file map, conventions
    2. Reference content only   — numbered workflows, looked up on demand
    3. No behavioral prose      — rules that "should" or "always" → moved to hooks
    4. No duplicated constraints — things enforced by hooks are not restated here
    5. Sub-directory delegation — module-specific rules in module-level CLAUDE.md files

  What was removed vs a typical CLAUDE.md (see README.md for the full before/after):
    × Prose behavioral rules ("Always add tests", "Never use magic strings")
    × Commit checklist (enforced by test_gate.sh hook)
    × Destructive command warnings (enforced by destructive_command_guard.sh hook)
    × Long onboarding prose
    × Duplicate project description
-->

## Project

FastAPI web service. Python 3.11. PostgreSQL via asyncpg. pytest for tests.

## Layout

```
src/
  api/
    routes/        # route handlers — one file per resource
    schemas/       # Pydantic request/response models
    deps.py        # FastAPI dependency injection
  core/
    config.py      # settings via pydantic-settings, reads from .env
    database.py    # asyncpg connection pool
  repositories/    # data access layer — one class per resource
  services/        # business logic — called by routes, calls repositories
tests/
  conftest.py      # shared fixtures (app, db session, test client)
  test_*.py        # mirrors src/ layout
.env               # local secrets — not committed
.env.example       # committed — shows required env vars with safe defaults
```

## Conventions

- Route handlers: validate input, call service, return schema. No business logic in routes.
- Services: orchestrate repositories. No direct DB queries in services.
- Repositories: one async method per DB operation. Return domain models, not raw rows.
- All database operations are async. Use `await` consistently.
- Pydantic models: `RequestModel` suffix for input, `ResponseModel` suffix for output.
- Environment variables: defined in `core/config.py`, never read directly with `os.environ`.

## File Map

| What you want | Where to look |
|---|---|
| Add a route | `src/api/routes/<resource>.py` |
| Add a schema | `src/api/schemas/<resource>.py` |
| Change DB queries | `src/repositories/<resource>_repository.py` |
| Change business logic | `src/services/<resource>_service.py` |
| Add a test fixture | `tests/conftest.py` |
| Change config / env | `src/core/config.py` + `.env.example` |

## Workflows

### Run tests
```bash
pytest tests/ -q
```

### Run locally
```bash
uvicorn src.main:app --reload
```

### Apply migrations
```bash
alembic upgrade head
```

### Create a new migration
```bash
alembic revision --autogenerate -m "describe the change"
```

## Session State

If `task_state.md` exists at the project root, read it before starting work.
After every significant step (file modified, test run, decision made), update it:
- Add a `Done` entry
- Update `Next Step` to the next concrete action
- Add anything deferred to `Open Questions`
