import json
import os

import pika
from pika.exceptions import AMQPError

EXCHANGE = "domain.events"
USER_DELETED = "user.deleted"

_RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
_UNREACHABLE_BROKER = "The event broker is unreachable."


class BrokerUnavailableError(Exception):
    def __init__(self) -> None:
        super().__init__(_UNREACHABLE_BROKER)


def publish(routing_key: str, event: dict[str, str]) -> None:
    try:
        connection = pika.BlockingConnection(
            pika.URLParameters(_RABBITMQ_URL)
        )
    except AMQPError as error:
        raise BrokerUnavailableError from error

    try:
        channel = connection.channel()
        channel.confirm_delivery()
        channel.exchange_declare(
            exchange=EXCHANGE, exchange_type="topic", durable=True
        )
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(event).encode(),
            properties=pika.BasicProperties(delivery_mode=2),
        )
    except AMQPError as error:
        raise BrokerUnavailableError from error
    finally:
        connection.close()
