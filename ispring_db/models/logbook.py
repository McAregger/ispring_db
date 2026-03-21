from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Logbook(SQLModel, table=True):
    __tablename__ = "logbook"

    log_id: Optional[int] = Field(default=None, primary_key=True)
    mac: str = Field(foreign_key="device.mac")

    log_date: date = Field(default_factory=date.today)
    log_author: str
    log_text: str

    device: Optional["Device"] = Relationship(back_populates="logs")


