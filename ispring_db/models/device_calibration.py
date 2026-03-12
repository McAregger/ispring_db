from datetime import date
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class DeviceCalibration(SQLModel, table=True):
    __tablename__ = "device_calibration"

    device_cal_id: Optional[int] = Field(default=None, primary_key=True)

    mac: str = Field(foreign_key="device.mac")
    cal_id: int = Field(foreign_key="calibration.cal_id")

    device_cal_status: str
    device_cal_date: date
    device_cal_filepath_tdms: str
    device_cal_total_error: str
    device_cal_station: str
    is_active: bool = False

    device: "Device" = Relationship(back_populates="device_calibrations")
    calibration: "Calibration" = Relationship(back_populates="device_calibrations")