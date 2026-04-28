# app/ — Application layer context

## Structural

This directory contains the core application logic: routes, models, validators, and the
Claude API client wrapper.

| File            | Responsibility                                              |
|-----------------|-------------------------------------------------------------|
| `routes.py`     | FastAPI route handlers — thin, delegates to helpers        |
| `models.py`     | Pydantic models — `EnrichmentRequest`, `EnrichmentResponse` |
| `client.py`     | Claude API wrapper — always forces `tool_choice: {type: tool}` |
| `validators.py` | Field-level validation — genre normalisation, confidence clamp |

Error taxonomy used across this layer:
- `422` — client sent invalid input (Pydantic catches at boundary)
- `502` — Claude returned output that failed validation
- `503` — Claude API unreachable

---

## Reference

### To add a field validator:
1. Add the `@field_validator` to the relevant model in `models.py`
2. Raise `ValueError` with a human-readable message on failure
3. Test both valid and invalid inputs in `tests/test_models.py`

### Claude client usage pattern:
```python
# Always use tool_choice to force structured output
response = client.enrich(text=request.text)   # returns EnrichmentResponse or raises
```

---

<!-- ──────────────────────────────────────────────────────────── -->
<!-- This sub-directory CLAUDE.md fires when Claude is working   -->
<!-- inside app/. The project root CLAUDE.md is also loaded —    -->
<!-- this file only adds app-layer detail (error taxonomy,       -->
<!-- module responsibilities, validator pattern).                -->
<!-- It does not repeat the project content map or workflows.    -->
<!-- ──────────────────────────────────────────────────────────── -->
