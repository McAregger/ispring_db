from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import Customer, License, CustomerLicense


@dataclass
class CustomerLicenseTableRow:
    customer_license_id: int
    customer: str
    license: str
    registration_date: str
    expiration_date: str


def get_all_customer_licenses() -> list[CustomerLicense]:
    with get_session() as session:
        statement = select(CustomerLicense).order_by(CustomerLicense.customer_license_id)
        return list(session.exec(statement).all())


def get_customer_license_by_id(customer_license_id: int) -> CustomerLicense | None:
    with get_session() as session:
        return session.get(CustomerLicense, customer_license_id)


def save_customer_license(customer_license: CustomerLicense) -> CustomerLicense:
    with get_session() as session:
        db_customer_license = session.merge(customer_license)
        session.add(db_customer_license)
        session.commit()
        session.refresh(db_customer_license)
        return db_customer_license


def delete_customer_license_by_id(customer_license_id: int) -> bool:
    with get_session() as session:
        customer_license = session.get(CustomerLicense, customer_license_id)

        if customer_license is None:
            return False

        session.delete(customer_license)
        session.commit()
        return True


def get_customer_license_rows() -> list[CustomerLicenseTableRow]:
    with get_session() as session:
        statement = (
            select(CustomerLicense, Customer, License)
            .join(Customer, CustomerLicense.customer_no == Customer.customer_no)
            .join(License, CustomerLicense.license_id == License.license_id)
            .order_by(Customer.company, License.license_name, License.license_release)
        )

        results = session.exec(statement).all()

        rows: list[CustomerLicenseTableRow] = []

        for customer_license, customer, license_obj in results:
            rows.append(
                CustomerLicenseTableRow(
                    customer_license_id=customer_license.customer_license_id,
                    customer=customer.company,
                    license=f"{license_obj.license_name} ({license_obj.license_release})",
                    registration_date=str(customer_license.registration_date),
                    expiration_date=str(customer_license.expiration_date or ""),
                )
            )

        return rows


def get_customer_license_rows_by_customer_no(
    customer_no: int,
) -> list[CustomerLicenseTableRow]:
    with get_session() as session:
        statement = (
            select(CustomerLicense, Customer, License)
            .join(Customer, CustomerLicense.customer_no == Customer.customer_no)
            .join(License, CustomerLicense.license_id == License.license_id)
            .where(CustomerLicense.customer_no == customer_no)
            .order_by(License.license_name, License.license_release)
        )

        results = session.exec(statement).all()

        rows: list[CustomerLicenseTableRow] = []

        for customer_license, customer, license_obj in results:
            rows.append(
                CustomerLicenseTableRow(
                    customer_license_id=customer_license.customer_license_id,
                    customer=customer.company,
                    license=f"{license_obj.license_name} ({license_obj.license_release})",
                    registration_date=str(customer_license.registration_date),
                    expiration_date=str(customer_license.expiration_date or ""),
                )
            )

        return rows