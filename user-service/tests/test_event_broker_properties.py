import json
from typing import final
from unittest import mock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pika.exceptions import AMQPError

from features.account.events import EXCHANGE, BrokerUnavailableError, publish

_BLOCKING_CONNECTION = "features.account.events.pika.BlockingConnection"
_UNREACHABLE_BROKER = "The event broker is unreachable."
_ROUTING_KEYS = st.sampled_from(["user.deleted", "user.created"])
_EVENTS = st.dictionaries(
    st.sampled_from(["user_id", "email"]),
    st.text(min_size=1, max_size=12),
    min_size=1,
)


@final
class RecordingChannel:
    def __init__(self) -> None:
        self.declared_exchange: str = ""
        self.published: dict[str, object] = {}

    def confirm_delivery(self) -> None:
        return None

    def exchange_declare(
        self, *, exchange: str, exchange_type: str, durable: bool
    ) -> None:
        _ = exchange_type
        _ = durable
        self.declared_exchange = exchange

    def basic_publish(
        self,
        *,
        exchange: str,
        routing_key: str,
        body: bytes,
        properties: object,
    ) -> None:
        _ = properties
        self.published = {
            "exchange": exchange,
            "routing_key": routing_key,
            "body": body,
        }


@final
class RecordingConnection:
    def __init__(self) -> None:
        self.opened_channel: RecordingChannel = RecordingChannel()
        self.closed: bool = False

    def channel(self) -> RecordingChannel:
        return self.opened_channel

    def close(self) -> None:
        self.closed = True


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=3))
def test___init___property_always_explains_the_unreachable_broker(
    count: int,
) -> None:
    errors = [BrokerUnavailableError() for _ in range(count)]

    assert all(str(error) == _UNREACHABLE_BROKER for error in errors)


@settings(max_examples=25)
@given(_ROUTING_KEYS, _EVENTS)
def test_publish_property_sends_the_event_and_closes_the_connection(
    routing_key: str, event: dict[str, str]
) -> None:
    connection = RecordingConnection()

    with mock.patch(_BLOCKING_CONNECTION, return_value=connection):
        publish(routing_key, event)

    published = connection.opened_channel.published
    body = published["body"]

    assert connection.opened_channel.declared_exchange == EXCHANGE
    assert published["exchange"] == EXCHANGE
    assert published["routing_key"] == routing_key
    assert isinstance(body, bytes)
    assert json.loads(body.decode()) == event
    assert connection.closed


@settings(max_examples=25)
@given(_ROUTING_KEYS, _EVENTS)
def test_publish_property_reports_a_broker_it_cannot_reach(
    routing_key: str, event: dict[str, str]
) -> None:
    with mock.patch(_BLOCKING_CONNECTION, side_effect=AMQPError):
        with pytest.raises(BrokerUnavailableError):
            publish(routing_key, event)
