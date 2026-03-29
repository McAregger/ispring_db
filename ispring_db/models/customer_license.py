from datetime import date
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship


class CustomerLicense(SQLModel, table=True):
    __tablename__ = "customer_license"

    __table_args__ = (
        UniqueConstraint(
            "customer_no",
            "license_id",
            name="uq_customer_license"
        ),
    )

    customer_license_id: Optional[int] = Field(default=None, primary_key=True)
    customer_no: int = Field(foreign_key="customer.customer_no")
    license_id: int = Field(foreign_key="license.license_id")

    registration_date: date
    expiration_date: Optional[date] = None

    customer: Optional["Customer"] = Relationship(
        back_populates="customer_license"
    )
    license: Optional["License"] = Relationship(
        back_populates="customer_license"
    )