# LeafLens API

<img src="https://img.shields.io/badge/version-1.0.0-5BC0DE?style=flat-square" alt="Version">&nbsp;
<img src="https://img.shields.io/badge/Python-3.12-5BC0DE?style=flat-square&logo=python&logoColor=white" alt="Python">&nbsp;
<img src="https://img.shields.io/badge/FastAPI-0.115-5BC0DE?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">&nbsp;
<img src="https://img.shields.io/badge/ThingsBoard-IoT-5BC0DE?style=flat-square" alt="ThingsBoard">&nbsp;
<img src="https://img.shields.io/badge/Supabase-Auth-5BC0DE?style=flat-square" alt="Supabase">

**FastAPI Backend for LeafLens Plant Health Monitoring System**

Part of Final Year Project — Bachelor of Computer Science, IIUM
**Supervisor:** Ts. Dr. Ahmad Anwar bin Zainuddin

---

## Overview

LeafLens API is the backend gateway for the LeafLens plant health monitoring
system. It sits between the Flutter mobile app and ThingsBoard IoT platform,
handling authentication, telemetry proxying, device management, and Growth
Health Score computation.

**What it does:**
- Verifies Supabase JWTs (via JWKS) — never issues tokens, only validates
- Proxies ThingsBoard REST API — Flutter never talks to ThingsBoard directly
- Relays RPC commands — Flutter -> API -> ThingsBoard -> ESP32
- Computes Growth Health Score (GHS) — weighted composite of sensor readings
- WebSocket relay — real-time telemetry from TB to Flutter

**What it does NOT do:**
- Does not store sensor data (ThingsBoard handles that)
- Does not manage user accounts (Supabase handles that)
- Does not talk to ESP32 directly (only via ThingsBoard MQTT)

---

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │                 Cloud / VPS                 │
                    │                                             │
  ┌──────────┐     │  ┌───────────┐     ┌──────────────────┐     │     ┌──────────┐
  │  ESP32   │─────┼─>│ ThingsBoard│<────│  leaflens-api    │<────┼─────│  Flutter  │
  │ (MQTT)   │     │  │  :8080    │     │  (FastAPI) :8000 │     │     │   App    │
  └──────────┘     │  └───────────┘     └──────────────────┘     │     └──────────┘
       │           │         ▲                    │               │          │
       │           │         │                    │               │          │
  Sensors +        │    TB REST API          DB + Auth            │     REST + WS
  Actuators        │    TB WebSocket         GHS Compute          │     JWT
                    │                                             │
                    │  ┌───────────┐     ┌──────────────────┐     │
                    │  │ PostgreSQL│     │    Supabase      │     │
                    │  │  :5432    │     │  (Auth only)     │     │
                    │  └───────────┘     └──────────────────┘     │
                    └─────────────────────────────────────────────┘
```

Full architecture details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Documentation

| Doc | Description |
|-----|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, data flows, tech stack |
| [API Reference](docs/API_REFERENCE.md) | All endpoints with request/response examples |
| [Conventions](docs/CONVENTIONS.md) | Coding standards, lint rules, commit format |
| [Project Structure](docs/PROJECT_STRUCTURE.md) | Directory layout, where to put code |
| [Error Handling](docs/ERROR_HANDLING.md) | Error hierarchy, Sentry integration |
| [Testing](docs/TESTING.md) | How to run and write tests |
| [GHS Algorithm](docs/GHS_ALGORITHM.md) | Growth Health Score formula and thresholds |
| [Domain Models](docs/DOMAIN_MODELS.md) | DB models, schemas, enums |
| [Environment](docs/ENVIRONMENT.md) | All env vars with descriptions |
| [Deployment](docs/DEPLOYMENT.md) | Local, Docker, mise setup |

---

## Prerequisites

- **Python 3.12+** (via mise or system)
- **PostgreSQL 16+**
- **ThingsBoard CE** (Docker or self-hosted)
- **Supabase** (project for auth)

---

## Getting Started

### 1. Clone and install

```bash
cd ~/Personal/Dev/leaflens-api

# Python version (via mise)
mise use python@3.12
eval "$(mise activate zsh)"

# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Dependencies
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your TB_API_KEY, SUPABASE_URL, etc.
```

### 3. Run

```bash
# Development (auto-reload)
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Verify

```bash
# Health probe
curl http://localhost:8000/api/v1/health

# Swagger UI (debug mode only)
open http://localhost:8000/docs
```

---

## Running Tests

```bash
DEBUG=true TB_API_KEY=test python -m pytest -v
```

### Test summary

```
tests/test_auth.py       — 1 test  (health probe)
tests/test_devices.py    — 1 test  (device list)
tests/test_ghs.py        — 3 tests (GHS computation)
tests/test_health.py     — 1 test  (health endpoint)
                        ─────────
                        6 passed
```

---

## Project Structure

```
leaflens-api/
├── app/
│   ├── main.py             # App factory + lifespan
│   ├── config.py           # pydantic-settings
│   ├── middleware.py        # Request ID + rate limiter
│   ├── auth/               # JWKS verification
│   ├── clients/            # ThingsBoard REST + WS
│   ├── db/                 # SQLAlchemy models
│   ├── routers/            # API endpoints
│   ├── schemas/            # Pydantic request/response
│   ├── services/           # GHS computation
│   └── utils/              # Error hierarchy
├── tests/                  # pytest async tests
├── alembic/                # DB migrations
├── docs/                   # Documentation
├── pyproject.toml          # ruff + mypy + pytest config
├── .pre-commit-config.yaml # Git hooks
├── Dockerfile              # Multi-stage build
└── docker-compose.yml      # Full stack
```

Full layout: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

---

## Linting & Type Checking

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy app/

# All pre-commit hooks
pre-commit run --all-files
```

**27 rule sets enabled.** Zero warnings, zero errors.

Full conventions: [docs/CONVENTIONS.md](docs/CONVENTIONS.md)

---

## Pre-commit Hooks

| Hook | What it does |
|------|-------------|
| ruff | Lint + auto-fix staged .py files |
| ruff-format | Format staged .py files |
| conventional-pre-commit | Enforce `type(scope): description` format |
| trailing-whitespace | Remove trailing spaces |
| end-of-file-fixer | Ensure newline at EOF |
| check-yaml / check-toml | Validate config files |
| check-added-large-files | Block files >500KB |
| check-merge-conflict | Detect unresolved merges |
| debug-statements | Block pdb/breakpoint in prod |

**Commit format:**
```
feat(backend): add WebSocket relay
fix(ghs): correct humidity weight
docs(api): update endpoint specs
```

Allowed scopes: `backend`, `auth`, `api`, `db`, `ghs`, `rpc`, `ws`, `docker`, `ci`, `deps`, `config`, `tests`, `middleware`

---

## Growth Health Score (GHS)

Weighted composite of sensor readings:

| Metric | Weight | Optimal Range |
|--------|--------|---------------|
| Soil Moisture | 50% | 40.0 - 80.0 |
| Temperature | 30% | 18.0 - 30.0 |
| Humidity | 20% | 40.0 - 80.0 |

| Score | Status |
|-------|--------|
| >= 80 | Optimal |
| >= 60 | Warning |
| >= 40 | Danger |
| < 40 | Critical |

Full algorithm: [docs/GHS_ALGORITHM.md](docs/GHS_ALGORITHM.md)

---

## Docker

```bash
# Full stack (PostgreSQL + FastAPI + ThingsBoard)
docker compose up -d

# Build only
docker compose build fastapi

# Logs
docker compose logs -f fastapi
```

---

## Hardware

This backend supports the LeafLens dual-ESP32 system:

| Sensor | Reading | Key |
|--------|---------|-----|
| Soil Moisture | Capacitive probe | `soil_moisture` |
| Temperature | DHT22 | `temperature` |
| Humidity | DHT22 | `humidity` |
| Water Level | Ultrasonic | `water_level` |

| Actuator | Control |
|----------|---------|
| Water Pump | RPC `triggerWatering` |
| Mist Maker | RPC `triggerMisting` |
| Solenoid Valve | RPC `openRefill` |

---

## Related Repositories

| Repository | Description |
|-----------|-------------|
| [LeafLens](https://github.com/mishoshup/LeafLens) | Flutter mobile app |
| LeafLens API | FastAPI backend (this repo) |
| [ThingsBoard](https://github.com/thingsboard/thingsboard) | IoT platform |

---

## License

This project is part of a Bachelor of Computer Science FYP at IIUM.
Internal use only — not licensed for distribution.
