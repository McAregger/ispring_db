from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import (
    Device,
    Logbook,
    DeviceCalibration,
    DeviceError,
)


def get_all_devices() -> list[Device]:
    with get_session() as session:
        return list(session.exec(select(Device)).all())


def get_devices_by_customer_no(customer_no: int) -> list[Device]:
    with get_session() as session:
        return list(
            session.exec(
                select(Device).where(Device.customer_no == customer_no)
            ).all()
        )


def get_device_by_mac(mac: str) -> Device | None:
    with get_session() as session:
        return session.get(Device, mac)


def save_device(device: Device) -> Device:
    with get_session() as session:
        db_obj = session.get(Device, device.mac)

        if db_obj is None:
            session.add(device)
            session.commit()
            session.refresh(device)
            return device

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


def get_device_dependencies_count(mac: str) -> dict[str, int]:
    with get_session() as session:
        logbook_count = len(
            session.exec(
                select(Logbook).where(Logbook.mac == mac)
            ).all()
        )

        calibration_count = len(
            session.exec(
                select(DeviceCalibration).where(DeviceCalibration.mac == mac)
            ).all()
        )

        error_count = len(
            session.exec(
                select(DeviceError).where(DeviceError.mac == mac)
            ).all()
        )

        return {
            "logbooks": logbook_count,
            "device_calibrations": calibration_count,
            "device_errors": error_count,
        }


def delete_device_by_mac(mac: str) -> bool:
    with get_session() as session:
        device = session.get(Device, mac)
        if device is None:
            return False

        logbooks = session.exec(
            select(Logbook).where(Logbook.mac == mac)
        ).all()

        device_calibrations = session.exec(
            select(DeviceCalibration).where(DeviceCalibration.mac == mac)
        ).all()

        device_errors = session.exec(
            select(DeviceError).where(DeviceError.mac == mac)
        ).all()

        for logbook in logbooks:
            session.delete(logbook)

        for device_calibration in device_calibrations:
            session.delete(device_calibration)

        for device_error in device_errors:
            session.delete(device_error)

        session.delete(device)
        session.commit()
        return True