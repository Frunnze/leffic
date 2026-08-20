import uuid
from collections.abc import Iterator
from unittest import mock

import pytest
import schemathesis
from hypothesis import HealthCheck, settings
from schemathesis import Case
from schemathesis.checks import not_a_server_error

from tests.property_fakes import FakeAiFactory, FakeAiManager
from tests.property_support import property_world
from tests.support import authorization

_CLIENT, _SESSIONS = property_world()
_CALLER = uuid.uuid4()
_CHATBOT_FACTORY = "features.chatbot.chatbot.ai_factory"

schema = schemathesis.openapi.from_asgi("/openapi.json", _CLIENT.app)


@pytest.fixture(autouse=True)
def _quiet_model() -> Iterator[None]:
    answering = FakeAiFactory(FakeAiManager({}, "an answer"))

    with mock.patch(_CHATBOT_FACTORY, answering):
        yield


@schema.parametrize()
@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=list(HealthCheck),
)
def test_api_contract_never_crashes_the_server(case: Case) -> None:
    case.call_and_validate(
        headers=authorization(str(_CALLER)),
        checks=[not_a_server_error],
    )
