"""Device endpoint tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.auth.dependencies import get_current_user
from app.db.engine import get_db


@pytest.mark.asyncio
async def test_list_devices_empty(client: AsyncClient) -> None:
    """Empty device list returns 200 with proper dependency overrides."""
    mock_db = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user-id",
        "email": "test@test.com",
    }
    app.dependency_overrides[get_db] = lambda: mock_db

    try:
        resp = await client.get(
            "/api/v1/devices",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()
