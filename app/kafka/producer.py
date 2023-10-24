import json

from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'localhost'})


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(
            msg.topic(), msg.partition()))


def produce_message(message: str, topic: str = "stripe", partition: int = None):
    p.poll(0)

    p.produce(topic, message.encode('utf-8'),
              partition=partition, callback=delivery_report)

    return p.flush()
