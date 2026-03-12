from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Gateway(SQLModel, table=True):
    __tablename__ = "gateway"

    serial_no: str = Field(primary_key=True)

    customer_no: Optional[int] = Field(
        default=None, foreign_key="customer.customer_no"
    )

    sim: Optional[bool] = None
    system: Optional[str] = None

    customer: Optional["Customer"] = Relationship(back_populates="gateways")