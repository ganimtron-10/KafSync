from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..sql import crud, database, schemas, models
from ..stripeapp import webhook as stripe_webhook

models.Base.metadata.create_all(bind=database.engine)

router = APIRouter(
    prefix='/customers',
    tags=['customers']
)


@router.post('/', response_model=schemas.Customer)
async def create_customer(customer: schemas.Customer, db: Session = Depends(database.get_db)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(
            status_code=400, detail="Email already registered")
    return crud.create_customer(db=db, customer=customer)


@router.get('/{customer_id}', response_model=schemas.Customer)
async def read_customer(customer_id: int, db: Session = Depends(database.get_db)):
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(
            status_code=404, detail="Customer not found")
    return db_customer


@router.put('/{customer_id}')
async def modify_customer(customer_id: int, customer: schemas.Customer, db: Session = Depends(database.get_db)):
    cnt = crud.update_customer(db, customer_id, customer)
    if not cnt:
        raise HTTPException(
            status_code=404, detail="Customer not found")
    return {"detail": "Customer updated Sucessfully"}


@router.delete('/{customer_id}', status_code=200)
async def remove_customer(customer_id: int, db: Session = Depends(database.get_db)):
    db_customer = crud.delete_customer(db, customer_id)
    if not db_customer:
        raise HTTPException(
            status_code=404, detail="Customer not found")
    return {"detail": "Customer deleted Sucessfully"}


@router.post('/webhook', status_code=200)
async def webhook(request: Request):
    payload = await request.json()
    try:
        stripe_webhook.handle_event(payload)
        return {"detail": "Event Sucessfully Captured"}
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=e)
