from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Device(SQLModel, table=True):
    __tablename__ = "device"

    mac: str = Field(primary_key=True)

    customer_no: Optional[int] = Field(default=None, foreign_key="customer.customer_no")

    manufacturing_date: date
    dms: str
    ble_antenna: str
    circuit_diagram_no: str
    revision: str
    assembly_plan: str
    bridge_layout: str
    batch_no: str

    customer: Optional["Customer"] = Relationship(back_populates="devices")

    device_calibrations: list["DeviceCalibration"] = Relationship(
        back_populates="device"
    )
    device_errors: list["DeviceError"] = Relationship(
        back_populates="device"
    )