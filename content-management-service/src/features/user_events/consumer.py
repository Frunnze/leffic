import os
from typing import Protocol

import pika
from pika.exceptions import AMQPError
from pydantic import BaseModel, ValidationError

from features.user_events.user_cleanup import remove_everything_owned_by
from shared.database import SessionLocal

EXCHANGE = "domain.events"
USER_DELETED = "user.deleted"
QUEUE = "content.user-deleted"

_RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


class Acknowledger(Protocol):
    def basic_ack(self, *, delivery_tag: int) -> None: ...


class Delivery(Protocol):
    @property
    def delivery_tag(self) -> int: ...


class UserDeleted(BaseModel):
    user_id: str


def handle(body: bytes) -> None:
    try:
        event = UserDeleted.model_validate_json(body)
    except ValidationError:
        return

    with SessionLocal() as db:
        _ = remove_everything_owned_by(db, event.user_id)


def consume() -> None:
    connection = pika.BlockingConnection(pika.URLParameters(_RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(
        exchange=EXCHANGE, exchange_type="topic", durable=True
    )
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(
        queue=QUEUE, exchange=EXCHANGE, routing_key=USER_DELETED
    )
    channel.basic_consume(queue=QUEUE, on_message_callback=_on_message)
    channel.start_consuming()


def _on_message(
    channel: Acknowledger,
    method: Delivery,
    _properties: object,
    body: bytes,
) -> None:
    try:
        handle(body)
    except AMQPError:
        return

    channel.basic_ack(delivery_tag=method.delivery_tag)
