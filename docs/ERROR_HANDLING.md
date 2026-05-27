# LeafLens API Error Handling

> Structured exceptions + JSON responses + Sentry integration.

---

## Architecture

```
  Request
     │
     v
  FastAPI Router
     │
     ├── LeafLensError raised ──> leaflens_error_handler
     │                                │
     │                                ├── Log (structured JSON)
     │                                ├── Sentry capture (if DSN set)
     │                                └── JSONResponse {error, type, request_id}
     │
     └── Unhandled exception ──> FastAPI default 500 handler
```

---

## Error Hierarchy

| Class | Status | Detail |
|-------|--------|--------|
| `LeafLensError` | 500 | "Internal server error" |
| `DeviceNotFoundError` | 404 | "Device not found" |
| `ThingsBoardError` | 502 | "ThingsBoard service unavailable" |
| `AuthError` | 401 | "Authentication failed" |

**Rules:**
- Always raise specific subclasses, never `LeafLensError` directly.
- Every error response includes `request_id` for tracing.
- Never expose internal details (stack traces, DB errors) to clients.

---

## Usage in Routers

```python
from app.utils.errors import DeviceNotFoundError

@router.get("/api/v1/devices/{device_id}")
async def get_device(device_id: str, ...):
    device = await db.get(device_id)
    if device is None:
        raise DeviceNotFoundError()
    return device
```

---

## Middleware Errors

| Middleware | Error | Response |
|-----------|-------|----------|
| RateLimitMiddleware | >60 RPM | 429 `{"error": "Rate limit exceeded", "retry_after": 60}` |
| RequestIDMiddleware | (never fails) | Adds `X-Request-ID` header |

---

## Sentry Integration

Optional. Controlled by `SENTRY_DSN` env var.

```bash
# Enable
SENTRY_DSN=https://xxx@sentry.io/123

# Disable (default)
SENTRY_DSN=
```

When enabled:
- 10% of transactions sampled (`traces_sample_rate=0.1`)
- PII not sent (`send_default_pii=False`)
- Environment tag: "development" or "production"
