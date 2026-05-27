"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserDevice(Base):
    """Maps Supabase users to ThingsBoard devices."""

    __tablename__ = "user_devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    tb_device_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    device_name: Mapped[str] = mapped_column(String(100))
    device_type: Mapped[str] = mapped_column(String(50), default="leaflens-env")
    mac_address: Mapped[str | None] = mapped_column(String(17), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
