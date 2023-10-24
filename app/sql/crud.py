import json

from sqlalchemy.orm import Session

from . import models, schemas
from ..kafka import producer


def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str):
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def create_customer(db: Session, customer: schemas.Customer):
    db_customer = models.Customer(email=customer.email, name=customer.name)
    db.add(db_customer)
    print(json.dumps(customer.json()))
    remaining_message = producer.produce_message(
        json.dumps(customer.json()), partition=0)
    if remaining_message == 0:
        db.commit()
        db.refresh(db_customer)
        return db_customer


def update_customer(db: Session, customer_id: int, customer: schemas.Customer):
    row_cnt = db.query(models.Customer).filter(models.Customer.id == customer_id).update(
        {models.Customer.name: customer.name, models.Customer.email: customer.email}, synchronize_session=False)
    print(json.dumps(customer.json()))
    remaining_message = producer.produce_message(
        json.dumps(customer.json()), partition=1)
    if remaining_message == 0:
        db.commit()
        return row_cnt


def delete_customer(db: Session, customer_id: int):
    row_cnt = db.query(models.Customer).filter(models.Customer.id ==
                                               customer_id).delete(synchronize_session=False)
    print(json.dumps(customer_id))
    remaining_message = producer.produce_message(
        json.dumps(customer_id), partition=2)
    if remaining_message == 0:
        db.commit()
        return row_cnt
