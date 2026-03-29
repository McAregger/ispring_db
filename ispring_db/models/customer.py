from typing import Optional
from sqlalchemy import CheckConstraint
from sqlmodel import SQLModel, Field, Relationship



class Customer(SQLModel, table=True):
    __tablename__ = "customer"
    __table_args__ = (
        CheckConstraint(
            "telephone GLOB '+41 [0-9][0-9] [0-9][0-9][0-9] [0-9][0-9] [0-9][0-9]'",
            name="ck_customer_telephone_format",
        ),
        CheckConstraint(
            "email GLOB '*@*.*[a-z][a-z]' OR email GLOB '*@*.*[a-z][a-z][a-z]'",
            name="ck_customer_email_format",
        ),
        CheckConstraint(
            "street GLOB '[a-zA-Z]*'",
            name="ck_only_letters"
        )
    )


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
    customer_license: list["CustomerLicense"] = Relationship(back_populates="customer")