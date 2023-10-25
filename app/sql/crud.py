import json

from typing import List
from sqlalchemy.orm import Session

from . import models, schemas
from ..kafka import producer


def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str):
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def get_all_customer_with_externalid(db: Session, external_ids: List):
    return db.query(models.Customer, models.IDMap).join(models.IDMap, models.Customer.id == models.IDMap.localid).all()


def create_customer(db: Session, customer: schemas.Customer, create_message: bool = True):
    db_customer = models.Customer(email=customer.email, name=customer.name)
    db.add(db_customer)
    db.flush()
    db.refresh(db_customer)
    if create_message:
        data = {
            "customer_id": db_customer.id,
            "customer": customer.model_dump()
        }
        producer.produce_message(
            json.dumps(data), topic="localtostripe", partition=0)
    db.commit()
    return db_customer


def update_customer(db: Session, customer_id: int, customer: schemas.Customer, create_message: bool = True):
    row_cnt = db.query(models.Customer).filter(models.Customer.id == customer_id).update(
        {models.Customer.name: customer.name, models.Customer.email: customer.email}, synchronize_session=False)
    if row_cnt > 0:
        if create_message:
            data = {
                "customer_id": customer_id,
                "customer": customer.model_dump()
            }
            producer.produce_message(
                json.dumps(data), topic="localtostripe", partition=1)
        db.commit()
        return row_cnt


def delete_customer(db: Session, customer_id: int, create_message: bool = True):
    row_cnt = db.query(models.Customer).filter(models.Customer.id ==
                                               customer_id).delete(synchronize_session=False)
    if row_cnt > 0:
        if create_message:
            data = {
                "customer_id": customer_id
            }
            producer.produce_message(
                json.dumps(data), topic="localtostripe", partition=2)

        db.commit()
        return row_cnt


def create_idmap(db: Session, localid: int, externalid: str):
    idmap_element = models.IDMap(localid=localid, externalid=externalid)
    db.add(idmap_element)
    db.commit()
    db.refresh(idmap_element)
    return idmap_element


def get_idmap_from_localid(db: Session, localid: int):
    return db.query(models.IDMap).filter(models.IDMap.localid == localid).first()


def get_idmap_from_externalid(db: Session, externalid: int):
    return db.query(models.IDMap).filter(models.IDMap.externalid == externalid).first()


def delete_idmap_by_localid(db: Session, localid: int):
    row_cnt = db.query(models.IDMap).filter(models.IDMap.localid ==
                                            localid).delete(synchronize_session=False)
    if row_cnt > 0:
        db.commit()
        return row_cnt
