from sqlmodel import select
from ispring_db.core.database import get_session
from ispring_db.models import Error

def get_all_errors():
    with get_session() as session:
        return session.exec(select(Error)).all()

def get_error_by_error_id(error_id):
    with get_session() as session:
        return session.get(Error, error_id)

def delete_error_by_error_id(error_id):
    with get_session() as session:
        error = session.get(Error, error_id)
        if error:
            session.delete(error)
            session.commit()

def save_error(error: Error) -> Error:
    with get_session() as session:
        if error.error_id is None:
            session.add(error)
            session.commit()
            session.refresh(error)
            return error

        db_obj = session.get(Error, error.error_id)

        if db_obj is None:
            session.add(error)
            session.commit()
            session.refresh(error)
            return error

        db_obj.component = error.component
        db_obj.error_cause = error.error_cause
        db_obj.error_severity = error.error_severity
        db_obj.repairability = error.repairability

        session.commit()
        session.refresh(db_obj)
        return db_obj






