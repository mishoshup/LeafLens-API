"""ThingsBoard WebSocket client for real-time relay."""

import asyncio
import json
import logging
import time
from collections.abc import Awaitable, Callable

import httpx
import websockets

from app.config import get_settings

logger = logging.getLogger(__name__)


class ThingsBoardWS:
    """Maintains a persistent WebSocket to ThingsBoard, relays telemetry."""

    def __init__(self) -> None:
        self._ws: websockets.ClientConnection | None = None
        self._subscribers: dict[str, list[Callable[[str, dict], Awaitable[None]]]] = {}
        self._running = False
        self._cmd_id = 0
        self._jwt_token = ""
        self._jwt_expires_at: float = 0
        self._device_subs: dict[int, str] = {}

    async def connect(self) -> None:
        settings = get_settings()
        await self._ensure_jwt()

        ws_url = settings.tb_ws_url
        self._ws = await websockets.connect(ws_url, ping_interval=None)

        # Authenticate
        await self._ws.send(json.dumps({"authCmd": {"cmdId": 0, "token": self._jwt_token}}))
        auth_resp = await self._ws.recv()
        logger.info("TB WebSocket authenticated: %s", auth_resp)

        self._running = True
        self._listen_task = asyncio.create_task(self._listen())
        self._keepalive_task = asyncio.create_task(self._keepalive())

    async def _ensure_jwt(self) -> None:
        """Acquire or refresh TB JWT. Valid for 2.5h, refresh at 2h."""
        if self._jwt_token and time.time() < self._jwt_expires_at:
            return

        settings = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.tb_url}/api/auth/login",
                json={"username": settings.tb_username, "password": settings.tb_password},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._jwt_token = data["token"]
            self._jwt_expires_at = time.time() + 7200
            logger.info("TB JWT acquired, expires in 7200s")

    async def subscribe(
        self, device_id: str, callback: Callable[[str, dict], Awaitable[None]]
    ) -> None:
        self._subscribers.setdefault(device_id, []).append(callback)

        self._cmd_id += 1
        self._device_subs[self._cmd_id] = device_id

        cmd = {
            "tsSubCmds": [
                {
                    "entityType": "DEVICE",
                    "entityId": device_id,
                    "scope": "LATEST_TELEMETRY",
                    "cmdId": self._cmd_id,
                }
            ],
        }
        await self._ws.send(json.dumps(cmd))  # type: ignore[union-attr]

    async def _listen(self) -> None:
        try:
            async for message in self._ws:  # type: ignore[union-attr]
                data = json.loads(message)
                if "data" not in data:
                    continue

                cmd_id = data.get("subscriptionId")
                device_id = self._device_subs.get(cmd_id, "unknown")

                for key, entries in data["data"].items():
                    ts_ms, value_str = entries[0]
                    payload = {"key": key, "ts": ts_ms, "value": float(value_str)}

                    for cb in self._subscribers.get(device_id, []):
                        asyncio.create_task(cb(key, payload))  # noqa: RUF006

        except websockets.ConnectionClosed:
            logger.warning("TB WebSocket closed — reconnecting in 5s")
            await asyncio.sleep(5)
            await self.connect()

    async def _keepalive(self) -> None:
        while self._running:
            await asyncio.sleep(get_settings().ws_keepalive_interval)
            try:
                await self._ensure_jwt()
                await self._ws.ping()  # type: ignore[union-attr]
            except Exception:
                break
