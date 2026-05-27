"""ThingsBoard REST API client (async httpx)."""

from typing import Any

import httpx

from app.config import get_settings


class ThingsBoardClient:
    """Async client for ThingsBoard REST API."""

    def __init__(self) -> None:
        s = get_settings()
        self.base_url = s.tb_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-Authorization": f"ApiKey {s.tb_api_key}"},
            timeout=httpx.Timeout(10.0),
        )

    async def close(self) -> None:
        await self._client.aclose()

    # ── Telemetry ───────────────────────────────────────────────────────

    async def get_latest_telemetry(self, device_id: str, keys: list[str]) -> dict[str, Any]:
        """Fetch latest values for given keys. Returns {key: value}."""
        resp = await self._client.get(
            f"/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries",
            params={"keys": ",".join(keys)},
        )
        resp.raise_for_status()
        raw: dict[str, list[dict[str, Any]]] = resp.json()
        return {key: float(entries[0]["value"]) for key, entries in raw.items() if entries}

    async def get_telemetry_history(
        self,
        device_id: str,
        keys: list[str],
        start_ts_ms: int,
        end_ts_ms: int,
        agg: str = "AVG",
        interval_ms: int = 3_600_000,
        limit: int = 2000,
    ) -> dict[str, list[dict[str, Any]]]:
        """Fetch historical telemetry. Returns {key: [{ts, value}, ...]}."""
        resp = await self._client.get(
            f"/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries",
            params={
                "keys": ",".join(keys),
                "startTs": start_ts_ms,
                "endTs": end_ts_ms,
                "limit": limit,
                "agg": agg,
                "interval": interval_ms,
                "orderBy": "ASC",
            },
        )
        resp.raise_for_status()
        return resp.json()

    # ── Attributes ──────────────────────────────────────────────────────

    async def get_shared_attributes(self, device_id: str) -> dict[str, Any]:
        resp = await self._client.get(
            f"/api/plugins/telemetry/DEVICE/{device_id}/values/attributes/SHARED_SCOPE",
        )
        resp.raise_for_status()
        return {entry["key"]: entry["value"] for entry in resp.json()}

    # ── RPC ─────────────────────────────────────────────────────────────

    async def send_rpc_oneway(
        self, device_id: str, method: str, params: dict | None = None
    ) -> None:
        resp = await self._client.post(
            f"/api/rpc/oneway/{device_id}",
            json={"method": method, "params": params or {}},
        )
        resp.raise_for_status()

    async def send_rpc_twoway(
        self,
        device_id: str,
        method: str,
        params: dict | None = None,
        timeout: int = 5000,
    ) -> dict[str, Any]:
        resp = await self._client.post(
            f"/api/rpc/twoway/{device_id}",
            json={"method": method, "params": params or {}, "timeout": timeout},
        )
        resp.raise_for_status()
        return resp.json()

    # ── Device Management ───────────────────────────────────────────────

    async def create_device(self, name: str, device_type: str = "sensor") -> dict[str, Any]:
        resp = await self._client.post(
            "/api/device",
            json={"name": name, "type": device_type},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_device_credentials(self, device_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"/api/device/{device_id}/credentials")
        resp.raise_for_status()
        return resp.json()

    async def get_device(self, device_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"/api/device/{device_id}")
        resp.raise_for_status()
        return resp.json()


_tb_client: ThingsBoardClient | None = None


def get_tb_client() -> ThingsBoardClient:
    """Singleton ThingsBoard client."""
    global _tb_client
    if _tb_client is None:
        _tb_client = ThingsBoardClient()
    return _tb_client
