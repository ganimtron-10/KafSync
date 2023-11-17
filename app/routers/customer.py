from typing import Dict

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
async def create_customer(customer: schemas.Customer, db: Session = Depends(database.get_db)) -> models.Customer:
    """
    Create a new customer in the local database.

    Parameters:
    - db (Session): SQLAlchemy database session.
    - customer (schemas.Customer): Customer data to be created.

    Returns:
    models.Customer: Created customer object.
    """
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(
            status_code=400, detail="Email already registered")
    try:
        return crud.create_customer(db=db, customer=customer)
    except:
        raise HTTPException(
            status_code=500, detail="Internal Server Error occured. Please try again later")


@router.get('/{customer_id}', response_model=schemas.Customer)
async def read_customer(customer_id: int, db: Session = Depends(database.get_db)) -> models.Customer:
    """
    Read customer details from the local database.

    Parameters:
    - customer_id (int): ID of the customer to be read.
    - db (Session): SQLAlchemy database session.

    Returns:
    models.Customer: Customer details.
    """
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(
            status_code=404, detail="Customer not found")
    return db_customer


@router.put('/{customer_id}')
async def modify_customer(customer_id: int, customer: schemas.Customer, db: Session = Depends(database.get_db)) -> Dict:
    """
    Modify an existing customer in the local database.

    Parameters:
    - customer_id (int): ID of the customer to be modified.
    - customer (schemas.Customer): Updated customer data.
    - db (Session): SQLAlchemy database session.

    Returns:
    dict: Detail of the modification.
    """
    update_cnt = None
    try:
        update_cnt = crud.update_customer(db, customer_id, customer)
    except:
        raise HTTPException(
            status_code=500, detail="Internal Server Error occured. Please try again later")

    if not update_cnt:
        raise HTTPException(
            status_code=404, detail="Customer not found")
    return {"detail": "Customer updated Sucessfully"}


@router.delete('/{customer_id}', status_code=200)
async def remove_customer(customer_id: int, db: Session = Depends(database.get_db)) -> Dict:
    """
    Remove a customer from the local database.

    Parameters:
    - customer_id (int): ID of the customer to be removed.
    - db (Session): SQLAlchemy database session.

    Returns:
    dict: Detail of the deletion.
    """
    db_customer = None
    try:
        db_customer = crud.delete_customer(db, customer_id)
    except:
        raise HTTPException(
            status_code=500, detail="Internal Server Error occured. Please try again later")
    if not db_customer:
        raise HTTPException(
            status_code=404, detail="Customer not found")
    return {"detail": "Customer deleted Sucessfully"}


@router.post('/webhook', status_code=200)
async def webhook(request: Request) -> Dict:
    """
    Handle incoming webhooks from Stripe.

    Parameters:
    - request (Request): FastAPI request object.

    Returns:
    dict: Detail of the webhook handling.
    """
    payload = await request.json()
    try:
        stripe_webhook.handle_event(payload)
        return {"detail": "Event Sucessfully Captured"}
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=e)
