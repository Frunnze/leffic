import json
from typing import Self, cast
from unittest import mock

import pika
from pika.exceptions import AMQPError
from sqlalchemy.orm import Session

from features.user_events import consumer


class FakeChannel:
    def __init__(self) -> None:
        super().__init__()
        self.bindings: list[tuple[str, str, str]] = []
        self.exchanges: list[str] = []
        self.queues: list[str] = []
        self.durable_queues: list[bool] = []
        self.durable_exchanges: list[bool] = []
        self.exchange_types: list[str] = []
        self.consumed: list[str] = []
        self.callbacks: list[object] = []
        self.acknowledged: list[int] = []
        self.started: bool = False

    def exchange_declare(
        self, *, exchange: str, exchange_type: str, durable: bool = False
    ) -> None:
        self.exchanges.append(exchange)
        self.exchange_types.append(exchange_type)
        self.durable_exchanges.append(durable)

    def queue_declare(self, *, queue: str, durable: bool = False) -> None:
        self.queues.append(queue)
        self.durable_queues.append(durable)

    def queue_bind(
        self, *, queue: str, exchange: str, routing_key: str
    ) -> None:
        self.bindings.append((queue, exchange, routing_key))

    def basic_consume(
        self, *, queue: str, on_message_callback: object
    ) -> None:
        self.consumed.append(queue)
        self.callbacks.append(on_message_callback)

    def basic_ack(self, *, delivery_tag: int) -> None:
        self.acknowledged.append(delivery_tag)

    def start_consuming(self) -> None:
        self.started = True


class FakeConnection:
    def __init__(self, channel: FakeChannel) -> None:
        super().__init__()
        self.fake_channel: FakeChannel = channel

    def channel(self: Self) -> FakeChannel:
        return self.fake_channel


class FakeMethod:
    def __init__(self, delivery_tag: int) -> None:
        super().__init__()
        self.delivery_tag: int = delivery_tag


def test_a_deletion_event_removes_that_users_content() -> None:
    with mock.patch.object(consumer, "remove_everything_owned_by") as remove:
        consumer.handle(json.dumps({"user_id": "u1"}).encode())

    assert isinstance(remove.call_args.args[0], Session)
    assert remove.call_args.args[1] == "u1"


def test_an_event_without_a_user_is_ignored() -> None:
    with mock.patch.object(consumer, "remove_everything_owned_by") as remove:
        consumer.handle(json.dumps({"nothing": True}).encode())

    assert remove.call_args is None


def test_an_event_that_is_not_an_object_is_ignored() -> None:
    with mock.patch.object(consumer, "remove_everything_owned_by") as remove:
        consumer.handle(json.dumps(["not", "an", "object"]).encode())

    assert remove.call_args is None


def test_the_consumer_binds_its_queue_to_the_deletion_key() -> None:
    channel = FakeChannel()

    with (
        mock.patch.object(
            pika, "BlockingConnection",
            return_value=FakeConnection(channel),
        ),
        mock.patch.object(pika, "URLParameters") as parameters,
    ):
        consumer.consume()

    url = cast("str", parameters.call_args.args[0])

    assert url.startswith("amqp://")
    assert channel.queues == [consumer.QUEUE]
    assert channel.bindings == [
        (consumer.QUEUE, consumer.EXCHANGE, consumer.USER_DELETED)
    ]
    assert channel.consumed == [consumer.QUEUE]
    assert channel.callbacks == [consumer._on_message]
    assert channel.started


def test_a_handled_message_is_acknowledged() -> None:
    channel = FakeChannel()

    with mock.patch.object(consumer, "remove_everything_owned_by"):
        consumer._on_message(
            channel,
            FakeMethod(7),
            None,
            json.dumps({"user_id": "u1"}).encode(),
        )

    assert channel.acknowledged == [7]


def test_a_message_that_fails_is_not_acknowledged() -> None:
    channel = FakeChannel()

    with mock.patch.object(
        consumer, "remove_everything_owned_by", side_effect=AMQPError("down")
    ):
        consumer._on_message(
            channel,
            FakeMethod(7),
            None,
            json.dumps({"user_id": "u1"}).encode(),
        )

    assert channel.acknowledged == []


def test_an_unreadable_message_is_dropped_rather_than_retried() -> None:
    channel = FakeChannel()

    consumer._on_message(channel, FakeMethod(7), None, b"not json")

    assert channel.acknowledged == [7]


def test_the_queue_and_exchange_survive_a_broker_restart() -> None:
    channel = FakeChannel()

    with (
        mock.patch.object(
            pika, "BlockingConnection",
            return_value=FakeConnection(channel),
        ),
        mock.patch.object(pika, "URLParameters"),
    ):
        consumer.consume()

    assert channel.exchanges == [consumer.EXCHANGE]
    assert channel.exchange_types == ["topic"]
    assert channel.durable_exchanges == [True]
    assert channel.durable_queues == [True]


def test_an_event_with_a_non_string_user_is_ignored() -> None:
    with mock.patch.object(consumer, "remove_everything_owned_by") as remove:
        consumer.handle(json.dumps({"user_id": 42}).encode())

    assert remove.call_args is None
