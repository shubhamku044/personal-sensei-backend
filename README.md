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

## Configuration

Settings are read from the environment with the `APP_` prefix (see `app/config.py`).
Copy `.env.example` to `.env` to override defaults locally.
