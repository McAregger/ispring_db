from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    customer_no: Optional[int] = Field(default=None, primary_key=True)

    company: str
    street: str
    street_number: str
    postcode: str
    city: str
    country: str
    contact_first_name: str
    contact_last_name: str
    telephone: str
    email: str

    devices: list["Device"] = Relationship(back_populates="customer")
    gateways: list["Gateway"] = Relationship(back_populates="customer")