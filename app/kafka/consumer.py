import json

from confluent_kafka import Consumer, Message


def handle_message(msg: Message):
    partition = msg.partition()
    if partition == 0:
        # Create
        data = json.loads(msg.value().decode('utf-8'))
        print(f"[Create] Message - {data['customer']}")
    elif partition == 1:
        # Update
        data = json.loads(msg.value().decode('utf-8'))
        print(f"[Update] Message - {data['customer_id']} - {data['customer']}")
    elif partition == 2:
        # Delete
        data = json.loads(msg.value().decode('utf-8'))
        print(f"[Delete] Message - {data['customer_id']}")
    else:
        print("Unable to handle this message")


c = Consumer({
    'bootstrap.servers': 'localhost',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['stripe'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    handle_message(msg)

c.close()
