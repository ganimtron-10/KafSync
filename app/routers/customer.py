from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..sql import crud, database, schemas, models

models.Base.metadata.create_all(bind=database.engine)

router = APIRouter(
    prefix='/customers',
    tags=['customers']
)


@router.post('/')
async def create_customer(customer: schemas.Customer, db: Session = Depends(database.get_db)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(
            status_code=400, detail="Email already registered")
    return crud.create_customer(db=db, customer=customer)


@router.get('/')
async def read_customer(customer_id: int, db: Session = Depends(database.get_db)):
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(
            status_code=404, detail="Customer not found")
    return db_customer
