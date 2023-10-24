import os

from dotenv import load_dotenv, find_dotenv
import stripe

from ..sql import schemas


load_dotenv(find_dotenv())

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_stripe_customer(customer: Customer):
    return stripe.Customer.create(name=customer.name, email=customer.email)


def get_stripe_customer(customer_id: str):
    return stripe.Customer.retrieve(id=customer_id)


def update_stripe_customer(customer_id: str, customer: Customer):
    return stripe.Customer.modify(id=customer_id, name=customer.name, email=customer.email)


def delete_stripe_customer(customer_id: str):
    return stripe.Customer.delete(customer_id)
