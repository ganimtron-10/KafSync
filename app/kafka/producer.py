import json

from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'localhost'})


def delivery_report(err, msg) -> None:
    """
    Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush().

    Parameters:
    - err: Delivery error (if any).
    - msg: Message object.

    Returns:
    None
    """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(
            msg.topic(), msg.partition()))


def produce_message(message: str, topic: str = None, partition: int = None) -> None:
    """
    Produce a message to a Kafka topic.

    Parameters:
    - message (str): Message content.
    - topic (str): Kafka topic to produce the message to.
    - partition (int): Kafka partition to use for message delivery.

    Returns:
    None
    """

    p.poll(0)

    p.produce(topic, message.encode('utf-8'),
              partition=partition, callback=delivery_report)

    return p.flush()
