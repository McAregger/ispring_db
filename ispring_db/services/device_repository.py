from ispring_db.core.database import get_session
from sqlmodel import select
from ispring_db.models import Device

def get_all_devices():
    with get_session() as session:
        devices = session.exec(select(Device)).all()
    return devices