from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class DeviceCalibration(SQLModel, table=True):
    __tablename__ = "device_calibration"

    device_cal_id: Optional[int] = Field(default=None, primary_key=True)

    mac: str = Field(foreign_key="device.mac")
    cal_id: int = Field(foreign_key="calibration.cal_id")

    calibration_date: date
    filepath_tdms: str
    total_error: str
    calibration_station: str

    device: Optional["Device"] = Relationship(
        back_populates="device_calibrations"
    )
    calibration: Optional["Calibration"] = Relationship(
        back_populates="device_calibrations"
    )