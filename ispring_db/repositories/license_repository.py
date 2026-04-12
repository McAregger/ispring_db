from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models.license import License


def get_all_licenses() -> list[License]:
    with get_session() as session:
        statement = select(License).order_by(License.license_name, License.license_release)
        return list(session.exec(statement).all())


def get_license_by_id(license_id: int) -> License | None:
    with get_session() as session:
        return session.get(License, license_id)


def save_license(license_obj: License) -> License:
    with get_session() as session:
        db_license = session.merge(license_obj)
        session.add(db_license)
        session.commit()
        session.refresh(db_license)
        return db_license


def delete_license_by_id(license_id: int) -> bool:
    with get_session() as session:
        license_obj = session.get(License, license_id)
        if license_obj is None:
            return False

        session.delete(license_obj)
        session.commit()
        return True