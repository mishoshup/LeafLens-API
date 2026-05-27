"""GHS endpoint tests."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.auth.dependencies import get_current_user


@pytest.mark.asyncio
async def test_health_score(client: AsyncClient) -> None:
    """Health score endpoint returns GHS."""
    mock_tb = AsyncMock()
    mock_tb.get_latest_telemetry.return_value = {
        "soil_moisture": 55.0,
        "temperature": 23.0,
        "humidity": 65.0,
    }

    from app.clients.thingsboard import get_tb_client
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user-id",
        "email": "test@test.com",
    }
    app.dependency_overrides[get_tb_client] = lambda: mock_tb

    try:
        resp = await client.get(
            "/api/v1/health/test-device-id",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "score" in data
        assert "status" in data
    finally:
        app.dependency_overrides.clear()
