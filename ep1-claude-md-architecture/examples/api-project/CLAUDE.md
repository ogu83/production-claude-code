# catalog-api

## What this repository is

FastAPI backend service that enriches movie catalog entries — accepts raw title and synopsis,
returns structured metadata (genres, sentiment, content rating) via Claude tool_use.

## Content map

| File / Directory       | Purpose                                             |
|------------------------|-----------------------------------------------------|
| `main.py`              | FastAPI app factory, lifespan hook                  |
| `app/routes.py`        | Request handlers — POST /api/enrich, GET /health    |
| `app/models.py`        | Pydantic request/response models                    |
| `app/client.py`        | Claude API wrapper — tool_use forced output         |
| `app/validators.py`    | Field-level validation helpers                      |
| `tests/`               | pytest suite — run with `pytest tests/ -v`          |
| `tests/integration/`   | Real Claude calls — run with `pytest -m integration`|

Stack: Python 3.12, FastAPI 0.110, Pydantic v2, Anthropic SDK 0.30

---

## Structural

<!-- ↑ Content map above — always relevant. -->

---

## Reference

### To add a new enrichment field:
1. Add the field to `EnrichmentResponse` in `app/models.py` (Pydantic)
2. Update the tool definition in `app/client.py` — add the field to `input_schema`
3. Add a field validator in `app/validators.py` if the field needs normalisation
4. Add a test case in `tests/test_models.py`

### To run locally:
```
uvicorn main:app --reload
```
API available at http://localhost:8000  
Swagger docs at http://localhost:8000/docs

### To run tests:
```
pytest tests/ -v                      # offline — no API key required
pytest tests/ -v -m integration      # real Claude calls
```

### To add a new endpoint:
1. Define Pydantic request/response models in `app/models.py`
2. Add the route function in `app/routes.py`
3. Wire Claude call through `app/client.py` — always use `tool_choice: {type: tool}`
4. Add tests in `tests/test_routes.py`

---

## Behavioral

Prefer typed returns. Keep route handlers under 30 lines — move logic to helpers.
