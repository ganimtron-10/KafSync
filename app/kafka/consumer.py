import json

from confluent_kafka import Consumer, Message


def handle_message(msg: Message):
    partition = msg.partition()
    if partition == 0:
        # Create
        print(f"[Create] Message - {msg.value()}")
        pass
    elif partition == 1:
        # Update
        print(f"[Update] Message - {msg.value()}")
        pass
    elif partition == 2:
        # Delete
        print(f"[Delete] Message - {msg.value()}")
        pass
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
