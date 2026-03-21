from ispring_db.models import DeviceCalibration, device_calibration
from ispring_db.core.database import get_session
from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import DeviceCalibration


def get_device_calibration_with_device_cal_id(device_cal_id: int):
    with get_session() as session:
        return session.get(DeviceCalibration, device_cal_id)


def save_device_calibration(device_calibration: DeviceCalibration) -> DeviceCalibration:
    with get_session() as session:
        is_new = device_calibration.device_cal_id is None

        if is_new:
            db_obj = DeviceCalibration()
            session.add(db_obj)
        else:
            db_obj = session.get(DeviceCalibration, device_calibration.device_cal_id)
            if db_obj is None:
                raise ValueError("Device calibration not found")

        db_obj.mac = device_calibration.mac
        db_obj.cal_id = device_calibration.cal_id
        db_obj.device_cal_status = device_calibration.device_cal_status
        db_obj.device_cal_date = device_calibration.device_cal_date
        db_obj.device_cal_filepath_tdms = device_calibration.device_cal_filepath_tdms
        db_obj.device_cal_total_error = device_calibration.device_cal_total_error
        db_obj.device_cal_station = device_calibration.device_cal_station
        db_obj.is_active = device_calibration.is_active

        session.commit()
        session.refresh(db_obj)
        return db_obj
