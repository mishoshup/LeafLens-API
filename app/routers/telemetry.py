"""Telemetry endpoints - latest and historical data."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user
from app.clients.thingsboard import ThingsBoardClient, get_tb_client

router = APIRouter()


@router.get("/api/v1/telemetry/{device_id}/latest")
async def get_latest_telemetry(
    device_id: str,
    user: dict = Depends(get_current_user),
    tb: ThingsBoardClient = Depends(get_tb_client),
) -> dict[str, object]:
    """Latest sensor readings for dashboard tiles."""
    data = await tb.get_latest_telemetry(
        device_id,
        keys=["soil_moisture", "temperature", "humidity", "water_level"],
    )
    return {"device_id": device_id, "readings": data}


@router.get("/api/v1/telemetry/{device_id}/history")
async def get_telemetry_history(
    device_id: str,
    days: int = Query(default=30, ge=1, le=90),
    user: dict = Depends(get_current_user),
    tb: ThingsBoardClient = Depends(get_tb_client),
) -> dict[str, object]:
    """30-day historical telemetry for trend charts.

    Uses 1-hour AVG aggregation - 720 points per key, well within limits.
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    data = await tb.get_telemetry_history(
        device_id,
        keys=["soil_moisture", "temperature", "humidity"],
        start_ts_ms=int(start.timestamp() * 1000),
        end_ts_ms=int(end.timestamp() * 1000),
        agg="AVG",
        interval_ms=3_600_000,
    )
    return {"device_id": device_id, "history": data}
