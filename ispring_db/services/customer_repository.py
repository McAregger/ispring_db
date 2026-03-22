from ispring_db.core.database import get_session
from sqlmodel import select
from ispring_db.models import Customer

def get_all_customers():
    with get_session() as session:
        customers = session.exec(select(Customer)).all()
        return customers

def get_customer_by_customer_no(customer_no):
    with get_session() as session:
        customer = session.get(Customer, customer_no)
        return customer

def delete_customer_by_customer_no(costumer_no):
    with get_session() as session:
        customer = get_customer_by_customer_no(costumer_no)
        session.delete(customer)
        session.commit()

def save_customer(customer: Customer) -> Customer:
    with get_session() as session:
        is_new = customer.customer_no is None

        if is_new:
            db_obj = Customer()

            first_customer = session.exec(
                select(Customer).order_by(Customer.customer_no)
            ).first()

            if first_customer is None:
                db_obj.customer_no = 1111

            session.add(db_obj)
        else:
            db_obj = session.get(Customer, customer.customer_no)

            if db_obj is None:
                raise ValueError("Selected customer could not be found.")

        db_obj.company = customer.company
        db_obj.street = customer.street
        db_obj.street_number = customer.street_number
        db_obj.postcode = customer.postcode
        db_obj.city = customer.city
        db_obj.country = customer.country
        db_obj.contact_first_name = customer.contact_first_name
        db_obj.contact_last_name = customer.contact_last_name
        db_obj.telephone = customer.telephone
        db_obj.email = customer.email

        session.commit()
        session.refresh(db_obj)
        return db_obj