# LeafLens API Environment Variables

Copy `.env.example` to `.env` and fill in values. Never commit `.env`.

---

## Variables

### Supabase (Auth)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| SUPABASE_URL | Yes (prod) | "" | `https://xyz.supabase.co` |
| SUPABASE_ANON_KEY | No | "" | Public anon key |
| SUPABASE_JWKS_URL | No | Auto-derived | Override JWKS endpoint |

### ThingsBoard

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| TB_URL | No | http://localhost:8080 | ThingsBoard base URL |
| TB_API_KEY | Yes | "" | API key (Tenant Settings) |
| TB_USERNAME | Yes | "" | Service account email |
| TB_PASSWORD | Yes | "" | Service account password |

### PostgreSQL

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | postgresql+asyncpg://... | Connection string |

### App

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DEBUG | No | false | Swagger UI, skip env validation |
| CORS_ORIGINS | No | ["http://localhost:3000"] | JSON array |
| WS_KEEPALIVE_INTERVAL | No | 30 | Seconds between TB pings |
| SENTRY_DSN | No | "" | Error tracking DSN |

---

## Getting Your ThingsBoard API Key

1. ThingsBoard UI -> API Keys (bottom-left sidebar)
2. Add New API Key -> name it `leaflens-backend`
3. Copy the key value
4. Set as `TB_API_KEY` in `.env`

The API key gives full tenant-level access. Keep it secret.

---

## Startup Validation

The app validates required env vars on startup in non-debug mode:
- Missing `TB_API_KEY` -> exits with error
- Missing `SUPABASE_URL` -> exits with error

In debug mode (`DEBUG=true`), validation is skipped.
