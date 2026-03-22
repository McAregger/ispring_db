from sqlmodel import select
from ispring_db.core.database import get_session
from ispring_db.models import Error

def get_all_errors():
    with get_session() as session:
        errors = session.exec(select(Error)).all()
        return errors