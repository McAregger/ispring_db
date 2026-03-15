from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class DeviceError(SQLModel, table=True):
    __tablename__ = "device_error"

    device_error_id: Optional[int] = Field(default=None, primary_key=True)

    mac: str = Field(foreign_key="device.mac")
    error_id: int = Field(foreign_key="error.error_id")

    device_error_date: date
    device_error_description: str

    device: Optional["Device"] = Relationship(back_populates="device_errors")
    error: Optional["Error"] = Relationship(back_populates="device_errors")