from PySide6.QtWidgets import QApplication

from ispring_db.core.database import get_session
from ispring_db.models import Calibration
from sqlmodel import Session, select

from ispring_db.models.device_calibration import DeviceCalibration
from ispring_db.models.device import Device

def get_all_calibrations():
    with get_session() as session:
        calibrations = session.exec(select(Calibration)).all()
    return calibrations

def get_calibration_with_cal_id(cal_id):
    with get_session() as session:
        calibration = session.get(Calibration, cal_id)
    return calibration

def delete_calibration_with_cal_id(cal_id):
    with get_session() as session:
        calibration = session.get(Calibration, cal_id)

        if calibration:
            session.delete(calibration)
            session.commit()


def save_calibration(calibration: Calibration) -> Calibration:
    with get_session() as session:
        is_new = calibration.cal_id is None

        if is_new:
            db_obj = Calibration()
            session.add(db_obj)
        else:
            db_obj = session.get(Calibration, calibration.cal_id)
            if db_obj is None:
                raise ValueError("Calibration not found")

        db_obj.cal_type = calibration.cal_type
        db_obj.min_temp = calibration.min_temp
        db_obj.max_temp = calibration.max_temp
        db_obj.cal_def_date = calibration.cal_def_date
        db_obj.cal_def_file = calibration.cal_def_file

        session.commit()
        session.refresh(db_obj)
        return db_obj







