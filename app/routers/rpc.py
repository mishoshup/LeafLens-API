"""RPC relay - Flutter -> FastAPI -> ThingsBoard -> ESP32."""

import httpx
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.clients.thingsboard import ThingsBoardClient, get_tb_client
from app.schemas.requests import RPCRequest

router = APIRouter()


@router.post("/api/v1/rpc/{device_id}")
async def send_rpc(
    device_id: str,
    body: RPCRequest,
    user: dict = Depends(get_current_user),
    tb: ThingsBoardClient = Depends(get_tb_client),
) -> dict[str, object]:
    """Relay RPC command from Flutter to ThingsBoard to ESP32.

    One-way for fire-and-forget (watering, misting).
    Two-way for commands needing confirmation.
    """
    try:
        if body.twoway:
            result = await tb.send_rpc_twoway(
                device_id, body.method, body.params, timeout=body.timeout
            )
            return {"device_id": device_id, "method": body.method, "result": result}
        await tb.send_rpc_oneway(device_id, body.method, body.params)
        return {"device_id": device_id, "method": body.method, "sent": True}
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 504:
            return {"device_id": device_id, "method": body.method, "queued": True}
        raise
