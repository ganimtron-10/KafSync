from sqlalchemy.orm import Session

from . import models, schemas


def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def create_customer(db: Session, user: schemas.Customer):
    db_user = models.Customer(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
