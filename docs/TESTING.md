# LeafLens API Testing Guide

> 6 tests. pytest + pytest-asyncio. Async test client via httpx ASGITransport.

---

## Running Tests

```bash
# Activate venv
source .venv/bin/activate

# Run all tests
DEBUG=true TB_API_KEY=test python -m pytest -v

# Run specific file
DEBUG=true TB_API_KEY=test python -m pytest tests/test_ghs.py -v

# Run with coverage
DEBUG=true TB_API_KEY=test python -m pytest --cov=app
```

**Why DEBUG=true?** Config validator exits on missing env vars in non-debug mode. Tests don't need real TB/Supabase.

---

## Test Directory

```
tests/
├── conftest.py        # Shared fixtures (async client)
├── test_auth.py       # Health probe
├── test_devices.py    # Device list endpoint
├── test_ghs.py        # GHS unit tests (pure computation)
└── test_health.py     # Health score endpoint
```

---

## Writing Tests

### Unit test (no mocks)

```python
def test_ghs_optimal() -> None:
    score, status, _ = compute_health_score(
        soil_moisture=60.0,
        temperature=24.0,
        humidity=65.0,
    )
    assert score >= 80.0
    assert status == GHSStatus.OPTIMAL
```

### Endpoint test (with dependency overrides)

```python
from app.auth.dependencies import get_current_user
from app.main import app

@pytest.mark.asyncio
async def test_list_devices(client: AsyncClient) -> None:
    app.dependency_overrides[get_current_user] = lambda: {"sub": "test-user-id"}

    try:
        resp = await client.get("/api/v1/devices")
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

**Rules:**
- Always use `app.dependency_overrides` for FastAPI deps, never `patch()` on the router.
- Always clear overrides in `finally` block.
- Use `MagicMock` for sync SQLAlchemy results, `AsyncMock` for async methods.
- Prefix unused variables with `_` (e.g., `_status`).

---

## Test Pyramid

```
         ╱╲
        ╱  ╲       Integration tests
       ╱ DB ╲      (endpoint + mock TB)
      ╱──────╲
     ╱        ╲    Unit tests
    ╱   GHS    ╲   (pure computation)
   ╱────────────╲
```

Most value is in GHS unit tests (pure logic, no deps). Endpoint tests verify wiring.
