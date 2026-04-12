from typing import Optional

from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import DeviceError, Device, Error


def get_all_device_errors() -> list[tuple[DeviceError, Device, Error]]:
    with get_session() as session:
        statement = (
            select(DeviceError, Device, Error)
            .join(Device, DeviceError.mac == Device.mac)
            .join(Error, DeviceError.error_id == Error.error_id)
        )
        return list(session.exec(statement).all())


def get_device_error_by_device_error_id(device_error_id: int) -> Optional[DeviceError]:
    with get_session() as session:
        return session.get(DeviceError, device_error_id)


def get_device_errors_by_customer_no(customer_no: int) -> list[tuple[DeviceError, Device, Error]]:
    with get_session() as session:
        statement = (
            select(DeviceError, Device, Error)
            .join(Device, DeviceError.mac == Device.mac)
            .join(Error, DeviceError.error_id == Error.error_id)
            .where(Device.customer_no == customer_no)
        )
        return list(session.exec(statement).all())


def save_device_error(device_error: DeviceError) -> DeviceError:
    with get_session() as session:
        if device_error.device_error_id is None:
            session.add(device_error)
            session.commit()
            session.refresh(device_error)
            return device_error

        db_obj = session.get(DeviceError, device_error.device_error_id)

        if db_obj is None:
            session.add(device_error)
            session.commit()
            session.refresh(device_error)
            return device_error

        db_obj.mac = device_error.mac
        db_obj.error_id = device_error.error_id
        db_obj.device_error_date = device_error.device_error_date
        db_obj.device_error_description = device_error.device_error_description

        session.commit()
        session.refresh(db_obj)
        return db_obj


def delete_device_error_by_id(device_error_id: int) -> bool:
    with get_session() as session:
        device_error = session.get(DeviceError, device_error_id)

        if device_error is None:
            return False

        session.delete(device_error)
        session.commit()
        return True




