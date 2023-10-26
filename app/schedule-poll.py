import time
import json

import schedule

from .stripeapp import crud as stripe_crud
from .sql import database, crud as sql_crud, schemas
from .kafka import producer

db = database.SessionLocal()


def sync_customer(customers):
    customer_list = []
    for customer in customers:
        customer_list.append(customer.id)
        localid = sql_crud.get_idmap_from_externalid(
            db, customer.id)
        local_customer = schemas.Customer(
            name=customer.name, email=customer.email)
        if localid is None:
            # create
            data = {
                "stripe_customer_id": customer.id,
                "customer": local_customer.model_dump()
            }
            producer.produce_message(
                json.dumps(data), topic="stripetolocal", partition=0)
        else:
            # update
            data = {
                "customer_id": localid.localid,
                "customer": local_customer.model_dump()
            }
            if not sql_crud.is_data_same(db, data["customer_id"], local_customer):
                producer.produce_message(
                    json.dumps(data), topic="stripetolocal", partition=1)

    # find customers to be deleted and delete it
    customer_idmap_list = sql_crud.get_all_customer_with_externalid(
        db, customer_list)
    for customer, idmap in customer_idmap_list:
        if idmap.externalid not in customer_list:
            data = {
                "customer_id": customer.id
            }
            producer.produce_message(
                json.dumps(data), topic="stripetolocal", partition=2)


def poll_stripe_customers():
    print("Polling started...")

    customers = stripe_crud.get_customer_list()

    if customers.get("error") is not None:
        print(stripe_customer_data)
        return

    sync_customer(customers)

    print("Polling completed successfully.")


schedule.every(10).seconds.do(poll_stripe_customers)

while True:
    schedule.run_pending()
    time.sleep(1)
