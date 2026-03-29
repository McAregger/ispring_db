from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

class Error(SQLModel, table=True):
    __tablename__ = "error"

    __table_args__ = (
        UniqueConstraint(
            "component",
            "error_cause",
            "error_severity",
            "repairability",
            name="uq_error_definition"
        ),
    )

    error_id: Optional[int] = Field(default=None, primary_key=True)

    component: str
    error_cause: str
    error_severity: int
    repairability: bool

    device_errors: list["DeviceError"] = Relationship(
        back_populates="error"
    )