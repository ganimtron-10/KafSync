import json

from confluent_kafka import Consumer, Message

from ..sql import database, schemas, crud as sql_crud
from ..stripeapp import crud as stripe_crud
from . import producer

db = database.SessionLocal()


def handle_topic_stripe_to_local(msg):
    partition = msg.partition()
    if partition == 0:
        # Create
        data = json.loads(msg.value().decode('utf-8'))
        customer = schemas.Customer(**data['customer'])
        stripe_cust_id = data["stripe_customer_id"]

        customer = sql_crud.create_customer(db, customer, create_message=False)
        print(
            f"Sucessfully Created Local Customer with local id {customer.id}")

        sql_crud.create_idmap(db, customer.id, stripe_cust_id)
        print(
            f"Sucessfully Created Id mapping of {customer.id} - {stripe_cust_id}")

    elif partition == 1:
        # Update
        data = json.loads(msg.value().decode('utf-8'))
        customer = schemas.Customer(**data['customer'])

        customer_id = data['customer_id']

        sql_crud.update_customer(
            db, customer_id, customer, create_message=False)

        print(
            f"Sucessfully Updated Local Customer with local id {customer_id}")

    elif partition == 2:
        # Delete
        data = json.loads(msg.value().decode('utf-8'))

        customer_id = data['customer_id']

        sql_crud.delete_customer(db, customer_id, create_message=False)

        print(
            f"Sucessfully Deleted Local Customer with local id {customer_id}")

    else:
        print("Unable to handle this message")


def handle_topic_local_to_stripe(msg):
    partition = msg.partition()
    if partition == 0:
        # Create
        data = json.loads(msg.value().decode('utf-8'))
        customer = schemas.Customer(**data['customer'])

        stripe_customer_data = stripe_crud.create_customer(customer)
        if stripe_customer_data.get("error") is not None:
            print(stripe_customer_data)
            return

        print(
            f"Sucessfully Created Stripe Customer with local id {data['customer_id']}")
        idmap = sql_crud.create_idmap(
            db, data['customer_id'], stripe_customer_data.id)
        print(
            f"Sucessfully Created Id mapping of {data['customer_id']} - {idmap.externalid}")
    elif partition == 1:
        # Update
        data = json.loads(msg.value().decode('utf-8'))
        customer = schemas.Customer(**data['customer'])

        stripe_cust_id = sql_crud.get_idmap_from_localid(db,
                                                         data['customer_id']).externalid
        stripe_customer_data = stripe_crud.update_customer(
            stripe_cust_id, customer)
        if stripe_customer_data.get("error") is not None:
            print(stripe_customer_data)
            return

        print(
            f"Sucessfully Updated Stripe Customer with local id {data['customer_id']}")
    elif partition == 2:
        # Delete
        data = json.loads(msg.value().decode('utf-8'))

        stripe_cust_id = sql_crud.get_idmap_from_localid(db,
                                                         data['customer_id']).externalid
        stripe_customer_data = stripe_crud.delete_customer(stripe_cust_id)
        if stripe_customer_data.get("error") is not None:
            print(stripe_customer_data)
            return

        print(
            f"Sucessfully Deleted Stripe Customer with local id {data['customer_id']}")
    else:
        print("Unable to handle this message")


def handle_message(msg: Message):
    topic = msg.topic()
    if topic == "localtostripe":
        handle_topic_local_to_stripe(msg)
    elif topic == "stripetolocal":
        handle_topic_stripe_to_local(msg)
    else:
        print(f"Can't Handle the topic {topic}")


c = Consumer({
    'bootstrap.servers': 'localhost',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})

c.subscribe(["localtostripe", "stripetolocal"])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    handle_message(msg)

c.close()
