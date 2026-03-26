from dataclasses import dataclass
from datetime import date, datetime

from sqlmodel import select

from ispring_db.core.database import get_session
from ispring_db.models import Logbook


@dataclass
class LogbookTableRow:
    log_id: str
    mac: str
    log_date: str
    log_author: str
    log_text: str


def _format_log_date(value) -> str:
    if value is None:
        return ""

    if isinstance(value, datetime):
        return value.strftime("%d.%m.%Y %H:%M:%S")

    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")

    return str(value)


def _build_logbook_table_rows(logs: list[Logbook]) -> list[LogbookTableRow]:
    rows: list[LogbookTableRow] = []

    for log in logs:
        rows.append(
            LogbookTableRow(
                log_id=str(log.log_id or ""),
                mac=str(log.mac or ""),
                log_date=_format_log_date(log.log_date),
                log_author=str(log.log_author or ""),
                log_text=str(log.log_text or ""),
            )
        )

    return rows


def get_log_by_id(log_id: int) -> Logbook | None:
    with get_session() as session:
        return session.get(Logbook, log_id)


def get_all_logs() -> list[Logbook]:
    with get_session() as session:
        statement = select(Logbook).order_by(
            Logbook.log_date.desc(),
            Logbook.log_id.desc(),
        )
        return list(session.exec(statement).all())


def get_logs_by_mac(mac: str) -> list[Logbook]:
    with get_session() as session:
        statement = (
            select(Logbook)
            .where(Logbook.mac == mac)
            .order_by(Logbook.log_date.desc(), Logbook.log_id.desc())
        )
        return list(session.exec(statement).all())


def get_logbook_table_rows() -> list[LogbookTableRow]:
    logs = get_all_logs()
    return _build_logbook_table_rows(logs)


def get_logbook_table_rows_by_mac(mac: str) -> list[LogbookTableRow]:
    logs = get_logs_by_mac(mac)
    return _build_logbook_table_rows(logs)


def save_log(log: Logbook) -> Logbook:
    with get_session() as session:
        if log.log_id is None:
            session.add(log)
            session.commit()
            session.refresh(log)
            return log

        db_obj = session.get(Logbook, log.log_id)

        if db_obj is None:
            new_log = Logbook(
                mac=log.mac,
                log_date=log.log_date,
                log_author=log.log_author,
                log_text=log.log_text,
            )
            session.add(new_log)
            session.commit()
            session.refresh(new_log)
            return new_log

        db_obj.mac = log.mac
        db_obj.log_date = log.log_date
        db_obj.log_author = log.log_author
        db_obj.log_text = log.log_text

        session.commit()
        session.refresh(db_obj)
        return db_obj


def delete_log(log_id: int) -> bool:
    with get_session() as session:
        db_obj = session.get(Logbook, log_id)

        if db_obj is None:
            return False

        session.delete(db_obj)
        session.commit()
        return True