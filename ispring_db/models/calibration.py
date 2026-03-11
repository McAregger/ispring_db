from datetime import date
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class Calibration(SQLModel, table=True):
    __tablename__ = "calibration"

    cal_id: Optional[int] = Field(default=None, primary_key=True)

    calibration_type: str
    min_temp: float
    max_temp: float
    cal_def_date: date
    cal_def_file: str

    device_calibrations: list["DeviceCalibration"] = Relationship(
        back_populates="calibration"
    )