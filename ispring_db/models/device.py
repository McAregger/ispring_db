from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Device(SQLModel, table=True):
    __tablename__ = "device"

    mac: str = Field(primary_key=True)
    customer_no: Optional[int] = Field(default=None, foreign_key="customer.customer_no")

    manufacturing_date: Optional[str] = None
    dms: Optional[str] = None
    ble_antenna: Optional[str] = None
    circuit_diagram_no: Optional[str] = None
    revision: Optional[str] = None
    assembly_plan: Optional[str] = None
    bridge_layout: Optional[str] = None
    batch_no: Optional[str] = None
    description: str | None = None

    customer: Optional["Customer"] = Relationship(back_populates="devices")

    logs: list["Logbook"] = Relationship(
        back_populates="device",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    device_calibrations: list["DeviceCalibration"] = Relationship(
        back_populates="device",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    device_errors: list["DeviceError"] = Relationship(
        back_populates="device",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
