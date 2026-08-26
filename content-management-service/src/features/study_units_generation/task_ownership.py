import hashlib
import hmac

from fastapi import HTTPException, status

from shared.jwt_secret import SECRET_KEY

MISSING_TASK = "Task does not exist!"

_SIGNATURE_DOMAIN = "leffic:study-unit-task-token:v1:"
_SEGMENT_SEPARATOR = "."
_TOKEN_SEGMENT_COUNT = 3
_TEXT_ENCODING = "utf-8"
_SURROGATE_HANDLING = "surrogatepass"
_AMBIGUOUS_SEGMENT = (
    "A task token segment may not contain the segment separator"
)


class AmbiguousTokenSegmentError(ValueError):
    def __init__(self, segment: str) -> None:
        super().__init__(f"{_AMBIGUOUS_SEGMENT}: {segment!r}")


def _encoded(text: str) -> bytes:
    return text.encode(_TEXT_ENCODING, _SURROGATE_HANDLING)


def _signature_of(task_id: str, folder_id: str) -> str:
    message = (
        f"{_SIGNATURE_DOMAIN}{task_id}{_SEGMENT_SEPARATOR}{folder_id}"
    )

    return hmac.new(
        _encoded(SECRET_KEY), _encoded(message), hashlib.sha256
    ).hexdigest()


def _refusal() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=MISSING_TASK
    )


def signed_task_id(task_id: str, folder_id: str) -> str:
    for segment in (task_id, folder_id):
        if _SEGMENT_SEPARATOR in segment:
            raise AmbiguousTokenSegmentError(segment)

    signature = _signature_of(task_id, folder_id)

    return _SEGMENT_SEPARATOR.join((task_id, folder_id, signature))


def verified_task_id(token: str) -> tuple[str, str]:
    segments = token.split(_SEGMENT_SEPARATOR)

    if len(segments) != _TOKEN_SEGMENT_COUNT:
        raise _refusal()

    task_id, folder_id, presented_signature = segments
    expected_signature = _signature_of(task_id, folder_id)

    if not hmac.compare_digest(
        _encoded(presented_signature), _encoded(expected_signature)
    ):
        raise _refusal()

    return task_id, folder_id
