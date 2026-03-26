from dataclasses import dataclass

from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import Gateway, Customer


@dataclass
class GatewayTableRow:
    serial_no: str
    customer: str
    sim: str
    system: str


def get_all_gateways() -> list[Gateway]:
    with get_session() as session:
        return list(session.exec(select(Gateway)).all())


def get_gateways_by_customer_no(customer_no: int) -> list[Gateway]:
    with get_session() as session:
        return list(
            session.exec(
                select(Gateway).where(Gateway.customer_no == customer_no)
            ).all()
        )


def get_gateway_by_serial_no(serial_no: str) -> Gateway | None:
    with get_session() as session:
        return session.get(Gateway, serial_no)


def save_gateway(gateway: Gateway) -> Gateway:
    with get_session() as session:
        if not gateway.serial_no:
            raise ValueError("Serial No is required.")

        serial_no = gateway.serial_no.strip()
        gateway.serial_no = serial_no

        db_obj = session.get(Gateway, serial_no)

        if db_obj is None:
            session.add(gateway)
            session.commit()
            session.refresh(gateway)
            return gateway

        db_obj.customer_no = gateway.customer_no
        db_obj.sim = gateway.sim
        db_obj.system = gateway.system

        session.commit()
        session.refresh(db_obj)
        return db_obj


def delete_gateway_by_serial_no(serial_no: str) -> bool:
    with get_session() as session:
        gateway = session.get(Gateway, serial_no)

        if gateway is None:
            return False

        session.delete(gateway)
        session.commit()
        return True


def _build_gateway_table_rows(gateways: list[Gateway]) -> list[GatewayTableRow]:
    with get_session() as session:
        rows: list[GatewayTableRow] = []

        for gateway in gateways:
            customer_text = ""

            if gateway.customer_no is not None:
                customer = session.get(Customer, gateway.customer_no)
                if customer:
                    customer_text = customer.company or str(customer.customer_no)
                else:
                    customer_text = str(gateway.customer_no)

            rows.append(
                GatewayTableRow(
                    serial_no=str(gateway.serial_no or ""),
                    customer=customer_text,
                    sim=str(gateway.sim or ""),
                    system=str(gateway.system or ""),
                )
            )

        return rows


def get_gateway_table_rows() -> list[GatewayTableRow]:
    gateways = get_all_gateways()
    return _build_gateway_table_rows(gateways)


def get_gateway_table_rows_by_customer_no(customer_no: int) -> list[GatewayTableRow]:
    gateways = get_gateways_by_customer_no(customer_no)
    return _build_gateway_table_rows(gateways)

