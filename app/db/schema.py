"""Pydantic schemas for DB models."""

from datetime import datetime

from pydantic import BaseModel


class UserDeviceRead(BaseModel):
    """Read model for user_devices table."""

    id: int
    user_id: str
    tb_device_id: str
    device_name: str
    device_type: str
    mac_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
