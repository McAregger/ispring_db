from ispring_db.core.database import get_session
from sqlmodel import select
from ispring_db.models import Device

def get_all_devices() -> list[Device]:
    with get_session() as session:
        devices = list(session.exec(select(Device)).all())
    return devices

def get_devices_by_customer_no(customer_no: int):
    with get_session() as session:
        devices = session.exec(
            select(Device).where(Device.customer_no == customer_no)
        ).all()
        return devices

def get_device_by_mac(mac: str):
    with get_session() as session:
        device = session.get(Device, mac)
        return device


def delete_device_by_mac(mac: str):
    with get_session() as session:
        device = session.get(Device, mac)
        if device is None:
            return False

        session.delete(device)
        session.commit()
        return True