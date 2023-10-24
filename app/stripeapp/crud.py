import os

from dotenv import load_dotenv, find_dotenv
import stripe

from ..sql import schemas


load_dotenv(find_dotenv())

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_customer(customer: schemas.Customer):
    try:
        return stripe.Customer.create(name=customer.name, email=customer.email)
    except:
        return {'error': "Unable to create Customer"}


def get_customer(customer_id: str):
    try:
        return stripe.Customer.retrieve(id=customer_id)
    except:
        return {'error': "Unable to get Customer"}


def update_customer(customer_id: str, customer: schemas.Customer):
    try:
        return stripe.Customer.modify(id=customer_id, name=customer.name, email=customer.email)
    except:
        return {'error': "Unable to update Customer"}


def delete_customer(customer_id: str):
    try:
        return stripe.Customer.delete(customer_id)
    except:
        return {'error': "Unable to delete Customer"}
