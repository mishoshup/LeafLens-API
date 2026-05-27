# LeafLens API Project Structure

---

## Directory Layout

```
leaflens-api/
├── app/
│   ├── __init__.py
│   ├── py.typed                  # PEP 561 marker
│   ├── main.py                   # App factory + lifespan
│   ├── config.py                 # pydantic-settings (all env vars)
│   ├── logging_config.py         # JSON structured logging
│   ├── middleware.py              # Request ID + rate limiter
│   ├── sentry.py                 # Optional error tracking
│   ├── auth/
│   │   ├── jwks.py               # Supabase JWT verify (cached)
│   │   └── dependencies.py       # get_current_user FastAPI dep
│   ├── clients/
│   │   ├── thingsboard.py        # TB REST client (httpx async)
│   │   └── tb_ws.py              # TB WebSocket (JWT auto-refresh)
│   ├── db/
│   │   ├── engine.py             # asyncpg pool + session factory
│   │   ├── models.py             # SQLAlchemy UserDevice model
│   │   └── schema.py             # Pydantic read models
│   ├── routers/
│   │   ├── devices.py            # POST register, GET list, GET detail
│   │   ├── telemetry.py          # GET latest, GET history
│   │   ├── health.py             # GET GHS score, GET summary
│   │   ├── rpc.py                # POST relay to ESP32
│   │   └── ws.py                 # WebSocket relay
│   ├── schemas/
│   │   ├── requests.py           # DeviceRegisterRequest, RPCRequest
│   │   ├── responses.py          # DeviceResponse, HealthScoreResponse
│   │   └── ws_messages.py        # WSMessageType enum
│   ├── services/
│   │   └── ghs.py                # Growth Health Score algorithm
│   └── utils/
│       └── errors.py             # LeafLensError hierarchy + handler
├── tests/
│   ├── conftest.py               # Shared fixtures (client)
│   ├── test_auth.py              # Health probe
│   ├── test_devices.py           # Device list
│   ├── test_ghs.py               # GHS unit tests
│   └── test_health.py            # Health endpoint
├── alembic/
│   ├── env.py                    # Async migration runner
│   └── versions/
├── docs/                         # This directory
├── .pre-commit-config.yaml       # Git hooks
├── pyproject.toml                # ruff + mypy + pytest + commitizen
├── requirements.txt              # Runtime dependencies
├── requirements-dev.txt          # Dev dependencies
├── alembic.ini                   # Alembic config
├── Dockerfile                    # Multi-stage build
├── docker-compose.yml            # Full stack
├── .gitignore
├── .gitattributes
└── .env.example                  # Template (never commit real values)
```

---

## Where to Put Code

| Type | Location | Example |
|------|----------|---------|
| New endpoint | `app/routers/` | `app/routers/alerts.py` |
| New DB model | `app/db/models.py` | Add class to existing file |
| New schema | `app/schemas/` | `app/schemas/alerts.py` |
| Business logic | `app/services/` | `app/services/alerts.py` |
| External API client | `app/clients/` | `app/services/email.py` |
| Custom error | `app/utils/errors.py` | Add subclass to existing file |
| Config field | `app/config.py` | Add to Settings class |
| Test | `tests/` | `test_alerts.py` |

---

## Code Generator

| Package | Version | Role |
|---------|---------|------|
| ruff | 0.8+ | Linting + formatting |
| mypy | 1.14+ | Static type checking |
| pre-commit | 4.0+ | Git hook manager |
| commitizen | 4.0+ | Conventional commits |
| pytest | 8.0+ | Test runner |
| pytest-asyncio | 0.24+ | Async test support |
