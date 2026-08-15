import uuid

import schemathesis
from hypothesis import HealthCheck, settings
from schemathesis import Case
from schemathesis.checks import not_a_server_error

from tests.property_support import property_client, signed_up_headers

_CLIENT = property_client()
_HEADERS = signed_up_headers(_CLIENT, uuid.uuid4(), "contract")

schema = schemathesis.openapi.from_asgi("/openapi.json", _CLIENT.app)


@schema.parametrize()
@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=list(HealthCheck),
)
def test_api_contract_never_crashes_the_server(case: Case) -> None:
    case.call_and_validate(headers=_HEADERS, checks=[not_a_server_error])
