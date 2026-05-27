"""Device management endpoints."""

import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.clients.thingsboard import ThingsBoardClient, get_tb_client
from app.db.engine import get_db
from app.db.models import UserDevice
from app.schemas.requests import DeviceRegisterRequest
from app.schemas.responses import DeviceResponse

router = APIRouter()

_TELEMETRY_KEYS = ["soil_moisture", "temperature", "humidity", "water_level"]


@router.post("/api/v1/devices/register")
async def register_device(
    body: DeviceRegisterRequest,
    tb: ThingsBoardClient = Depends(get_tb_client),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Register a new ESP32 device after BLE onboarding.

    Creates TB device, saves mapping, returns TB access token.
    """
    tb_device = await tb.create_device(name=body.device_name, device_type="sensor")
    tb_device_id: str = tb_device["id"]["id"]

    creds = await tb.get_device_credentials(tb_device_id)
    access_token: str = creds["credentialsId"]

    device = UserDevice(
        user_id=body.user_id,
        tb_device_id=tb_device_id,
        device_name=body.device_name,
        mac_address=body.mac_address,
    )
    db.add(device)
    await db.commit()

    return {"thingsboard_token": access_token, "device_id": tb_device_id}


@router.get("/api/v1/devices", response_model=list[DeviceResponse])
async def list_devices(
    user: dict = Depends(get_current_user),
    tb: ThingsBoardClient = Depends(get_tb_client),
    db: AsyncSession = Depends(get_db),
) -> list[DeviceResponse]:
    """List all devices belonging to the current user, with latest telemetry."""
    result = await db.execute(select(UserDevice).where(UserDevice.user_id == user["sub"]))
    devices = result.scalars().all()

    tasks = [tb.get_latest_telemetry(d.tb_device_id, _TELEMETRY_KEYS) for d in devices]
    readings = await asyncio.gather(*tasks, return_exceptions=True)

    response: list[DeviceResponse] = []
    for device, reading in zip(devices, readings, strict=True):
        latest = reading if not isinstance(reading, Exception) else None
        response.append(
            DeviceResponse(
                id=device.id,
                tb_device_id=device.tb_device_id,
                device_name=device.device_name,
                device_type=device.device_type,
                latest_readings=latest,
            )
        )
    return response


@router.get("/api/v1/devices/{device_id}")
async def get_device(
    device_id: str,
    user: dict = Depends(get_current_user),
    tb: ThingsBoardClient = Depends(get_tb_client),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Get single device details + latest telemetry."""
    result = await db.execute(
        select(UserDevice).where(
            UserDevice.tb_device_id == device_id,
            UserDevice.user_id == user["sub"],
        )
    )
    device = result.scalar_one_or_none()
    if device is None:
        return {"error": "Device not found"}

    readings = await tb.get_latest_telemetry(device_id, _TELEMETRY_KEYS)
    return {
        "id": device.id,
        "tb_device_id": device.tb_device_id,
        "device_name": device.device_name,
        "device_type": device.device_type,
        "latest_readings": readings,
    }
