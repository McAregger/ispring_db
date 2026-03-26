from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import Device


def get_all_devices() -> list[Device]:
    with get_session() as session:
        devices = list(session.exec(select(Device)).all())
    return devices


def get_devices_by_customer_no(customer_no: int) -> list[Device]:
    with get_session() as session:
        devices = session.exec(
            select(Device).where(Device.customer_no == customer_no)
        ).all()
        return list(devices)


def get_device_by_mac(mac: str) -> Device | None:
    with get_session() as session:
        device = session.get(Device, mac)
        return device


def save_device(device: Device) -> Device:
    with get_session() as session:
        db_obj = session.get(Device, device.mac)

        if db_obj is None:
            # INSERT
            session.add(device)
            session.commit()
            session.refresh(device)
            return device

        # UPDATE
        db_obj.customer_no = device.customer_no
        db_obj.manufacturing_date = device.manufacturing_date
        db_obj.dms = device.dms
        db_obj.ble_antenna = device.ble_antenna
        db_obj.circuit_diagram_no = device.circuit_diagram_no
        db_obj.revision = device.revision
        db_obj.assembly_plan = device.assembly_plan
        db_obj.bridge_layout = device.bridge_layout
        db_obj.batch_no = device.batch_no
        db_obj.description = device.description

        session.commit()
        session.refresh(db_obj)
        return db_obj


def delete_device_by_mac(mac: str) -> bool:
    with get_session() as session:
        device = session.get(Device, mac)
        if device is None:
            return False

        session.delete(device)
        session.commit()
        return True