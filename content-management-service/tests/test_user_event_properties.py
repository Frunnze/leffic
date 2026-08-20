import json
import uuid
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st
from pika.exceptions import AMQPError
from sqlalchemy.orm import Session

from features.user_events import consumer as consumer_module
from features.user_events.consumer import (
    EXCHANGE,
    QUEUE,
    USER_DELETED,
    _on_message,
    consume,
    handle,
)
from features.user_events.user_cleanup import (
    _stored_file_names,
    remove_everything_owned_by,
)
from shared.models import Folder
from tests.amqp_fakes import FakeAmqpConnection
from tests.folder_seeding import seeded_folder
from tests.support import in_memory_sessions

_BLOCKING_CONNECTION = "features.user_events.consumer.pika.BlockingConnection"
_FILE_COUNTS = st.integers(min_value=0, max_value=3)


def _folder_count(session: Session, owner: uuid.UUID) -> int:
    return session.query(Folder).filter(Folder.user_id == owner).count()


class _RecordingChannel:
    def __init__(self) -> None:
        self.acknowledged: list[int] = []

    def basic_ack(self, *, delivery_tag: int) -> None:
        self.acknowledged.append(delivery_tag)


class _Delivery:
    def __init__(self, delivery_tag: int) -> None:
        self._delivery_tag: int = delivery_tag

    @property
    def delivery_tag(self) -> int:
        return self._delivery_tag


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _FILE_COUNTS)
def test__stored_file_names_property_names_one_file_per_stored_row(
    owner: uuid.UUID, file_count: int
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        _ = seeded_folder(session, owner, {"file": file_count})
        names = _stored_file_names(session, owner)

    assert len(names) == file_count
    assert all(name.endswith(".pdf") for name in names)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids(), _FILE_COUNTS)
def test_remove_everything_owned_by_property_spares_every_other_owner(
    owner: uuid.UUID, stranger: uuid.UUID, file_count: int
) -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        _ = seeded_folder(session, owner, {"file": file_count})
        _ = seeded_folder(session, stranger, {"file": file_count})
        mine_before = _folder_count(session, owner)
        theirs_before = _folder_count(session, stranger)
        removed = remove_everything_owned_by(session, str(owner))
        mine_after = _folder_count(session, owner)
        theirs_after = _folder_count(session, stranger)

    assert removed == mine_before
    assert mine_after == 0
    assert theirs_after == theirs_before


@settings(max_examples=25)
@given(st.uuids())
def test_handle_property_cleans_up_after_a_well_formed_event(
    user_id: uuid.UUID,
) -> None:
    body = json.dumps({"user_id": str(user_id)}).encode()

    with (
        mock.patch.object(consumer_module, "SessionLocal"),
        mock.patch.object(
            consumer_module, "remove_everything_owned_by"
        ) as cleanup,
    ):
        handle(body)

    assert cleanup.call_args.args[1] == str(user_id)


@settings(max_examples=25)
@given(st.sampled_from([b"", b"{}", b"not json", b'{"user_id": 4}']))
def test_handle_property_ignores_an_event_it_cannot_read(
    body: bytes,
) -> None:
    with mock.patch.object(
        consumer_module, "remove_everything_owned_by"
    ) as cleanup:
        handle(body)

    assert not cleanup.called


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=50))
def test_consume_property_binds_the_queue_to_the_user_deleted_events(
    delivery_tag: int,
) -> None:
    _ = delivery_tag

    connection = FakeAmqpConnection()

    with mock.patch(_BLOCKING_CONNECTION, return_value=connection):
        consume()

    channel = connection.opened_channel

    assert channel.declared_exchange == EXCHANGE
    assert channel.bound == {
        "queue": QUEUE,
        "exchange": EXCHANGE,
        "routing_key": USER_DELETED,
    }


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=50))
def test__on_message_property_acknowledges_only_what_it_handled(
    delivery_tag: int,
) -> None:
    channel = _RecordingChannel()

    with mock.patch.object(consumer_module, "handle"):
        _on_message(channel, _Delivery(delivery_tag), None, b"{}")

    with mock.patch.object(
        consumer_module, "handle", side_effect=AMQPError
    ):
        _on_message(channel, _Delivery(delivery_tag + 1), None, b"{}")

    assert channel.acknowledged == [delivery_tag]


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=50))
def test_basic_ack_property_records_every_tag_it_is_handed(
    delivery_tag: int,
) -> None:
    channel = _RecordingChannel()
    channel.basic_ack(delivery_tag=delivery_tag)

    assert channel.acknowledged == [delivery_tag]


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=50))
def test_delivery_tag_property_reports_the_tag_it_was_built_with(
    delivery_tag: int,
) -> None:
    assert _Delivery(delivery_tag).delivery_tag == delivery_tag
