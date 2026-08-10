from typing import Self, cast
from unittest import mock

import pytest
import requests

from features.file_upload import content_client

_FILE_METADATA = [{"file_id": "abc", "name": "notes.pdf", "extension": "pdf"}]
_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"


class FakeResponse:
    def __init__(self, failure: Exception | None = None) -> None:
        super().__init__()
        self.failure: Exception | None = failure

    def raise_for_status(self: Self) -> None:
        if self.failure is not None:
            raise self.failure


def test_registering_files_posts_them_to_the_content_service() -> None:
    with mock.patch.object(
        requests, "post", return_value=FakeResponse()
    ) as post:
        content_client.register_files(_FILE_METADATA, _FOLDER_ID)

    assert post.call_args.kwargs["json"] == {
        "file_metadata": _FILE_METADATA,
        "folder_id": _FOLDER_ID,
    }
    url = cast("str", post.call_args.kwargs["url"])

    assert url.endswith("/save-file-names")
    assert post.call_args.kwargs["timeout"] == content_client._TIMEOUT_SECONDS


def test_a_refused_registration_raises() -> None:
    failure = requests.HTTPError("nope")

    with (
        mock.patch.object(
            requests, "post", return_value=FakeResponse(failure)
        ),
        pytest.raises(requests.HTTPError),
    ):
        content_client.register_files(_FILE_METADATA, None)
