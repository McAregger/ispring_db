from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Error(SQLModel, table=True):
    __tablename__ = "error"

    error_id: Optional[int] = Field(default=None, primary_key=True)

    component: str
    error_cause: str
    error_severity: int
    repairability: int

    device_errors: list["DeviceError"] = Relationship(
        back_populates="error"
    )