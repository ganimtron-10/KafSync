import os
from typing import Dict, Union, List

from dotenv import load_dotenv, find_dotenv
import stripe

from ..sql import schemas


load_dotenv(find_dotenv())

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_customer(customer: schemas.Customer) -> Union[Dict, stripe.Customer]:
    """
    Create a new customer on the Stripe platform.

    Parameters:
    - customer (schemas.Customer): Customer data for creation.

    Returns:
    dict or stripe.Customer: Created customer data or error details.
    """

    try:
        return stripe.Customer.create(name=customer.name, email=customer.email)
    except Exception as e:
        return {'error': "Unable to create Customer", 'details': e}


def get_customer(customer_id: str) -> Union[Dict, stripe.Customer]:
    """
    Retrieve customer data from the Stripe platform.

    Parameters:
    - customer_id (str): ID of the customer to retrieve.

    Returns:
    dict or stripe.Customer: Retrieved customer data or error details.
    """
    try:
        return stripe.Customer.retrieve(id=customer_id)
    except Exception as e:
        return {'error': "Unable to get Customer", 'details': e}


def get_customer_list() -> Union[Dict, List[stripe.Customer]]:
    """
    Retrieve a list of customers from the Stripe platform.

    Returns:
    dict or List[stripe.Customer]: List of customer data or error details.
    """
    try:
        return stripe.Customer.list()
    except Exception as e:
        return {'error': "Unable to get Customer", 'details': e}


def update_customer(customer_id: str, customer: schemas.Customer) -> Union[Dict, stripe.Customer]:
    """
    Update an existing customer on the Stripe platform.

    Parameters:
    - customer_id (str): ID of the customer to update.
    - customer (schemas.Customer): Updated customer data.

    Returns:
    dict or stripe.Customer: Updated customer data or error details.
    """
    try:
        return stripe.Customer.modify(id=customer_id, name=customer.name, email=customer.email)
    except Exception as e:
        return {'error': "Unable to update Customer", 'details': e}


def delete_customer(customer_id: str) -> Union[Dict, stripe.Customer]:
    """
    Delete a customer from the Stripe platform.

    Parameters:
    - customer_id (str): ID of the customer to delete.

    Returns:
    dict or stripe.Deleted: Deletion confirmation or error details.
    """
    try:
        return stripe.Customer.delete(customer_id)
    except Exception as e:
        return {'error': "Unable to delete Customer", 'details': e}
