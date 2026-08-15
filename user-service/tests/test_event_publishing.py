import json
from typing import Self, cast
from unittest import mock

import pika
import pytest
from pika.exceptions import AMQPError

from features.account import events


class FakeChannel:
    def __init__(self) -> None:
        super().__init__()
        self.published: list[dict[str, object]] = []
        self.exchanges: list[str] = []
        self.exchange_types: list[str] = []
        self.durable_exchanges: list[bool] = []
        self.delivery_modes: list[int] = []
        self.confirmed: bool = False

    def confirm_delivery(self) -> None:
        self.confirmed = True

    def exchange_declare(
        self, *, exchange: str, exchange_type: str, durable: bool = False
    ) -> None:
        self.exchanges.append(exchange)
        self.exchange_types.append(exchange_type)
        self.durable_exchanges.append(durable)

    def basic_publish(
        self,
        *,
        exchange: str,
        routing_key: str,
        body: bytes,
        properties: pika.BasicProperties | None = None,
    ) -> None:
        if properties is not None:
            self.delivery_modes.append(properties.delivery_mode)

        self.published.append(
            {
                "exchange": exchange,
                "routing_key": routing_key,
                "body": body.decode(),
            }
        )


class FakeConnection:
    def __init__(self, channel: FakeChannel) -> None:
        super().__init__()
        self.fake_channel: FakeChannel = channel
        self.closed: bool = False

    def channel(self: Self) -> FakeChannel:
        return self.fake_channel

    def close(self) -> None:
        self.closed = True


def test_an_event_is_published_to_the_topic_exchange() -> None:
    channel = FakeChannel()
    connection = FakeConnection(channel)

    with mock.patch.object(
        pika, "BlockingConnection", return_value=connection
    ):
        events.publish(events.USER_DELETED, {"user_id": "u1"})

    assert channel.exchanges == [events.EXCHANGE]
    assert channel.published[0]["routing_key"] == events.USER_DELETED
    assert json.loads(str(channel.published[0]["body"])) == {"user_id": "u1"}


def test_publishing_waits_for_the_broker_to_confirm() -> None:
    channel = FakeChannel()
    connection = FakeConnection(channel)

    with mock.patch.object(
        pika, "BlockingConnection", return_value=connection
    ):
        events.publish(events.USER_DELETED, {"user_id": "u1"})

    assert channel.confirmed


def test_the_connection_is_always_closed() -> None:
    channel = FakeChannel()
    connection = FakeConnection(channel)

    with mock.patch.object(
        pika, "BlockingConnection", return_value=connection
    ):
        events.publish(events.USER_DELETED, {"user_id": "u1"})

    assert connection.closed


def test_an_unreachable_broker_is_reported() -> None:
    with (
        mock.patch.object(
            pika, "BlockingConnection", side_effect=AMQPError("down")
        ),
        pytest.raises(events.BrokerUnavailableError) as refusal,
    ):
        events.publish(events.USER_DELETED, {"user_id": "u1"})

    assert str(refusal.value) == "The event broker is unreachable."


def test_the_broker_is_reached_at_the_configured_url() -> None:
    channel = FakeChannel()

    with (
        mock.patch.object(
            pika, "BlockingConnection", return_value=FakeConnection(channel)
        ),
        mock.patch.object(pika, "URLParameters") as parameters,
    ):
        events.publish(events.USER_DELETED, {"user_id": "u1"})

    url = cast("str", parameters.call_args.args[0])

    assert url.startswith("amqp://")


def test_a_refused_publish_is_reported() -> None:
    channel = FakeChannel()
    connection = FakeConnection(channel)

    with (
        mock.patch.object(
            pika, "BlockingConnection", return_value=connection
        ),
        mock.patch.object(
            FakeChannel, "basic_publish", side_effect=AMQPError("refused")
        ),
        pytest.raises(events.BrokerUnavailableError),
    ):
        events.publish(events.USER_DELETED, {"user_id": "u1"})

    assert connection.closed


def test_the_exchange_and_message_survive_a_broker_restart() -> None:
    channel = FakeChannel()
    connection = FakeConnection(channel)

    with mock.patch.object(
        pika, "BlockingConnection", return_value=connection
    ):
        events.publish(events.USER_DELETED, {"user_id": "u1"})

    assert channel.exchange_types == ["topic"]
    assert channel.durable_exchanges == [True]
    assert channel.delivery_modes == [2]


def test_the_event_goes_to_the_shared_exchange() -> None:
    channel = FakeChannel()
    connection = FakeConnection(channel)

    with mock.patch.object(
        pika, "BlockingConnection", return_value=connection
    ):
        events.publish(events.USER_DELETED, {"user_id": "u1"})

    assert channel.published[0]["exchange"] == "domain.events"
    assert channel.published[0]["routing_key"] == "user.deleted"
