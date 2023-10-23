from sqlalchemy.orm import Session

from . import models, schemas


def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str):
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def create_customer(db: Session, customer: schemas.Customer):
    db_customer = models.Customer(email=customer.email, name=customer.name)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer
