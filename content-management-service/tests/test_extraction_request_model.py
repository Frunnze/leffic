import inspect
from collections.abc import Mapping
from typing import cast

from features.study_units_generation.text_sources import (
    FileMetadata,
    StoredDocument,
)

_FILE_ID = "6f1c7d4e-0000-4000-8000-00000000000a"


def test_file_metadata_has_no_extension_field() -> None:
    assert set(FileMetadata.model_fields) == {"file_id", "pages"}


def test_a_client_supplied_extension_never_reaches_file_metadata() -> None:
    described = FileMetadata.model_validate(
        {"file_id": _FILE_ID, "extension": "../../etc/passwd"}
    )

    assert not hasattr(described, "extension")


def test_stored_document_is_a_field_only_model() -> None:
    namespace = cast("Mapping[str, object]", vars(StoredDocument))
    declared_methods = [
        name
        for name, attribute in namespace.items()
        if inspect.isfunction(attribute)
    ]

    assert set(StoredDocument.model_fields) == {
        "storage_name",
        "extension",
        "pages",
    }
    assert declared_methods == []
