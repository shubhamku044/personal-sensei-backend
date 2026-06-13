# Personal Sensei — Backend

FastAPI service managed with [uv](https://docs.astral.sh/uv/).

## Requirements

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Setup

```bash
uv sync                   # install runtime + dev dependencies
uv run pre-commit install # enable git pre-commit hooks
```

## Run

```bash
# Hot-reloading dev server (recommended):
uv run fastapi dev app/main.py

# or via the entry script:
uv run python main.py
```

The API is served at http://127.0.0.1:8000 — interactive docs at `/docs`.

### Health check

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","app":"Personal Sensei API","version":"0.1.0","environment":"development"}
```

## Quality tooling ("no mercy")

| Tool | Purpose             | Command                |
| ---- | ------------------- | ---------------------- |
| Ruff | Lint (`select=ALL`) | `uv run ruff check .`  |
| Ruff | Format              | `uv run ruff format .` |
| mypy | Strict typing       | `uv run mypy`          |

All three run automatically on commit via pre-commit.

## Architecture

Service-layered. Cross-cutting concerns live in `app/core/`:

```
app/
├── api/routes/      # HTTP layer — thin; parses requests, calls services
├── services/        # business logic; raises app.core.errors.* on failure
├── repositories/    # persistence / data access
├── agent/           # LLM agent + tools
└── core/            # config, logging, errors, middleware (cross-cutting)
```

### Errors

Raise typed errors from any layer — never build error responses by hand:

```python
from app.core.errors import NotFoundError

raise NotFoundError("session 42 not found", details={"id": 42})
```

Registered handlers turn every `AppError` (and unexpected exceptions) into a
consistent JSON body: `{"code": "...", "message": "...", "details": {...}}`.
Subclasses: `NotFoundError`, `ValidationError`, `ConflictError`,
`UnauthorizedError`, `ForbiddenError`, `ExternalServiceError`.

### Logging

Configured once at startup via `app.core.logging.configure_logging()`. Get a
module logger with `get_logger(__name__)`. Every request is logged with method,
path, status and latency by the middleware in `app/core/middleware.py`.

## Configuration

Settings are read from the environment with the `APP_` prefix (see
`app/core/config.py`). Copy `.env.example` to `.env` to override defaults locally.
