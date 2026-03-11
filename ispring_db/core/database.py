from sqlmodel import SQLModel, Session, create_engine
from ispring_db.core.config import DATABASE_URL
import ispring_db.models as models


engine = create_engine(DATABASE_URL,
                       echo=False,
                       connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)


if __name__ == "__main__":
    create_db_and_tables()

    customer = models.Customer(
        company="ispring Systems AG",
        street="Bergstrasse",
        street_number="12",
        postcode="8618",
        city="Oetwil am See",
        country = "Switzerland",
        contact_first_name="Boris",
        contact_last_name="Ouriev",
        telephone="+41 44 929 68 28",
        email="boris.ouriev@ispring.ch"

    )

    with get_session() as session:
        session.add(customer)
        session.commit()
        session.refresh(customer)

    print(customer)