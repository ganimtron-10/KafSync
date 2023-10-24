import os

from dotenv import load_dotenv, find_dotenv
import stripe

from ..sql import schemas


load_dotenv(find_dotenv())

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_stripe_customer(customer: Customer):
    return stripe.Customer.create(name=customer.name, email=customer.email)
