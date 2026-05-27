# LeafLens API Deployment

---

## Local Development

```bash
# 1. Clone and setup
cd ~/Personal/Dev/leaflens-api
mise use python@3.12
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 2. Configure
cp .env.example .env
# Edit .env with your TB_API_KEY, SUPABASE_URL, etc.

# 3. Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Test
open http://localhost:8000/docs   # Swagger UI (debug mode only)
DEBUG=true TB_API_KEY=test python -m pytest -v
```

---

## Pre-commit Hooks

```bash
# Install (one-time)
pre-commit install --hook-type pre-commit --hook-type commit-msg

# Run manually on all files
pre-commit run --all-files

# Run on staged files only
git add .
git commit -m "feat: your message"
# Hooks run automatically
```

**Hooks:**
1. ruff — lint + auto-fix staged .py files
2. ruff-format — format staged .py files
3. conventional-pre-commit — enforce feat/fix/chore format
4. trailing-whitespace, end-of-file-fixer, check-yaml, etc.

---

## Docker

```bash
# Build
docker compose build

# Run full stack (PostgreSQL + FastAPI + ThingsBoard)
docker compose up -d

# Check logs
docker compose logs -f fastapi

# Stop
docker compose down
```

---

## Mise (Python Version)

```bash
# Check current
mise current python

# Install Python 3.12
mise install python@3.12

# Activate in shell (add to ~/.zshrc)
eval "$(mise activate zsh)"

# Pin for this project
mise use python@3.12
```

---

## Environment Variables

See `docs/ENVIRONMENT.md` for full reference. Key vars:

| Variable | Required | Description |
|----------|----------|-------------|
| TB_API_KEY | Yes | ThingsBoard API key |
| SUPABASE_URL | Yes (prod) | Supabase project URL |
| DATABASE_URL | Yes | PostgreSQL connection string |
| DEBUG | No | Enables Swagger UI, skips env validation |
| SENTRY_DSN | No | Error tracking |
