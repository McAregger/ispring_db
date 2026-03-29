from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

class License(SQLModel, table=True):
    __tablename__ = "license"

    __table_args__ = (
        UniqueConstraint(
            "license_name",
            "license_release",
            name="uq_license_definition"
        ),
    )

    license_id: Optional[int] = Field(default=None, primary_key=True)
    license_name: str
    license_release: str


    customer_license: list["CustomerLicense"] = Relationship(
        back_populates="license"
    )