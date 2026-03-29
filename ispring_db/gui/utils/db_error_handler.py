from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from PySide6.QtWidgets import QMessageBox, QWidget


def get_db_error_message(error: Exception) -> tuple[str, str]:
    text = str(error)

    # Gateway
    if "ck_gateway_serial_no_format" in text:
        return (
            "Invalid Serial No",
            "Serial No must start with 4G or 5G and be followed by exactly 4 digits.\n"
            "Example: 4G0001 or 5G0002",
        )


    if "ck_customer_telephone_format" in text:
        return (
            "Invalid Phone Format",
            "Not a valid Phone Number\n"
            "Example: +41 44 796 66 66",
        )

    if "ck_customer_email_format" in text:
        return (
            "Invalid Email Format",
            "Not a valid Email Address"
        )

    if "ck_only_letters" in text:
        return (
            "Invalid Street Address",
            "Only Letters allowed.",
        )

    if "NOT NULL constraint failed: device_error.error_id" in text:
        return (
            "Delete not possible",
            "This error cannot be deleted because it is still assigned to device errors.",
        )



    return (
        "Database Error",
        text,
    )


def show_db_error(parent: QWidget | None, error: Exception) -> None:
    title, message = get_db_error_message(error)
    QMessageBox.warning(parent, title, message)


def handle_db_error(parent: QWidget | None, error: Exception) -> None:
    if isinstance(error, IntegrityError):
        show_db_error(parent, error)

        return

    QMessageBox.critical(parent, "Unexpected Error", str(error))