"""WebSocket relay - TB -> FastAPI -> Flutter."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth.jwks import verify_supabase_token
from app.config import get_settings

router = APIRouter()


@router.websocket("/api/v1/ws")
async def ws_relay(websocket: WebSocket) -> None:
    """WebSocket relay: TB -> FastAPI -> Flutter.

    Auth: JWT passed as query param ?token=...
    """
    settings = get_settings()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        verify_supabase_token(token, settings.jwks_url, settings.supabase_url)
    except Exception:
        await websocket.close(code=4003, reason="Invalid token")
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "subscribe":
                device_id = data["device_id"]
                await websocket.send_json({"type": "subscribed", "device_id": device_id})
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        pass
