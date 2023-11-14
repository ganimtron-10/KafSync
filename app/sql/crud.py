import json

from typing import List, Tuple
from sqlalchemy.orm import Session

from . import models, schemas
from ..kafka import producer


def get_customer(db: Session, customer_id: int) -> models.Customer:
    """
    Get customer details from the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - customer_id (int): ID of the customer to be retrieved.

    Returns:
    models.Customer: Customer details.
    """
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str) -> models.Customer:
    """
    Get customer details by email from the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - email (str): Email of the customer to be retrieved.

    Returns:
    models.Customer: Customer details.
    """
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def get_all_customer_with_externalid(db: Session, external_ids: List) -> List[Tuple[models.Customer, models.IDMap]]:
    """
    Get a list of customers with their external IDs from the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - external_ids (List): List of external IDs.

    Returns:
    List[Tuple[models.Customer, models.IDMap]]: List of customer and IDMap tuples.
    """
    return db.query(models.Customer, models.IDMap).join(models.IDMap, models.Customer.id == models.IDMap.localid).all()


def create_customer(db: Session, customer: schemas.Customer, create_message: bool = True) -> models.Customer:
    """
    Create a new customer in the local database and produce a Kafka message.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - customer (schemas.Customer): Customer data to be created.
    - create_message (bool, optional): Flag to indicate whether to create a Kafka message. Defaults to True.

    Returns:
    models.Customer: Created customer object.
    """
    msg_sucess = None
    db_customer = models.Customer(email=customer.email, name=customer.name)
    try:
        with db.begin_nested():
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
                msg_sucess = True
        return db_customer
    except Exception as e:
        print(e)
        if msg_sucess:
            # reverting the produced message action
            data = {
                "customer_id": db_customer.id
            }
            producer.produce_message(
                json.dumps(data), topic="localtostripe", partition=2)


def update_customer(db: Session, customer_id: int, customer: schemas.Customer, create_message: bool = True) -> int:
    """
    Update an existing customer in the local database and produce a Kafka message.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - customer_id (int): ID of the customer to be updated.
    - customer (schemas.Customer): Updated customer data.
    - create_message (bool, optional): Flag to indicate whether to create a Kafka message. Defaults to True.

    Returns:
    int: Number of rows updated.
    """
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


def delete_customer(db: Session, customer_id: int, create_message: bool = True) -> int:
    """
    Delete a customer from the local database and produce a Kafka message.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - customer_id (int): ID of the customer to be deleted.
    - create_message (bool, optional): Flag to indicate whether to create a Kafka message. Defaults to True.

    Returns:
    int: Number of rows deleted.
    """
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


def create_idmap(db: Session, localid: int, externalid: str) -> models.IDMap:
    """
    Create an IDMap entry in the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - localid (int): Local ID.
    - externalid (str): External ID.

    Returns:
    models.IDMap: Created IDMap object.
    """
    idmap_element = models.IDMap(localid=localid, externalid=externalid)
    db.add(idmap_element)
    db.commit()
    db.refresh(idmap_element)
    return idmap_element


def get_idmap_from_localid(db: Session, localid: int) -> models.IDMap:
    """
    Get IDMap details by local ID from the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - localid (int): Local ID.

    Returns:
    models.IDMap: IDMap details.
    """
    return db.query(models.IDMap).filter(models.IDMap.localid == localid).first()


def get_idmap_from_externalid(db: Session, externalid: int) -> models.IDMap:
    """
    Get IDMap details by external ID from the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - externalid (int): External ID.

    Returns:
    models.IDMap: IDMap details.
    """
    return db.query(models.IDMap).filter(models.IDMap.externalid == externalid).first()


def delete_idmap_by_localid(db: Session, localid: int) -> int:
    """
    Delete an IDMap entry by local ID from the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - localid (int): Local ID.

    Returns:
    int: Number of rows deleted.
    """
    row_cnt = db.query(models.IDMap).filter(models.IDMap.localid ==
                                            localid).delete(synchronize_session=False)
    if row_cnt > 0:
        db.commit()
        return row_cnt


def is_data_same(db: Session, customer_id: int, customer: models.Customer) -> bool:
    """
    Check if the given customer data is the same as the existing data in the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - customer_id (int): ID of the customer to be checked.
    - customer (models.Customer): Customer data to be checked.

    Returns:
    bool: True if the data is the same, False otherwise.
    """
    existing_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id).first()

    if existing_customer:
        return existing_customer.name == customer.name and existing_customer.email == customer.email

    return False
