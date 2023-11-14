import json
import os

import stripe
from dotenv import load_dotenv, find_dotenv

from ..kafka import producer
from ..sql import schemas


load_dotenv(find_dotenv())

stripe.api_key = os.getenv("STRIPE_API_KEY")


def handle_event(payload: bytes) -> None:
    """
    Handle a Stripe event and produce Kafka messages for customer-related events.

    Parameters:
    - payload (dict): Stripe event payload.

    Returns:
    None
    """
    event = None

    try:
        event = stripe.Event.construct_from(payload, stripe.api_key)
    except ValueError as e:
        raise Exception("Invalid Payload")

    # Handle the event
    if event.type == 'customer.created':
        customer = event.data.object

        data = {
            "stripe_customer_id": customer.id,
            "customer": {"name": customer.name, "email": customer.email}
        }
        producer.produce_message(
            json.dumps(data), topic="stripetolocal", partition=0)

    elif event.type == 'customer.updated':
        customer = event.data.object

        data = {
            "stripe_customer_id": customer.id,
            "customer": {"name": customer.name, "email": customer.email}
        }
        producer.produce_message(
            json.dumps(data), topic="stripetolocal", partition=1)
    elif event.type == 'customer.deleted':
        customer = event.data.object

        data = {
            "stripe_customer_id": customer.id
        }
        producer.produce_message(
            json.dumps(data), topic="stripetolocal", partition=2)
    else:
        raise Exception('Unhandled event type {}'.format(event.type))
