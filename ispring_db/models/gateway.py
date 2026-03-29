from typing import Optional

from sqlalchemy import CheckConstraint
from sqlmodel import SQLModel, Field, Relationship


class Gateway(SQLModel, table=True):
    __tablename__ = "gateway"
    __table_args__ = (
        CheckConstraint(
            "serial_no GLOB '[45]G[0-9][0-9][0-9][0-9]'",
            name="ck_gateway_serial_no_format",
        ),
    )

    serial_no: str = Field(primary_key=True)
    customer_no: Optional[int] = Field(default=None, foreign_key="customer.customer_no")

    sim: Optional[bool] = None
    system: Optional[str] = None

    customer: Optional["Customer"] = Relationship(back_populates="gateways")