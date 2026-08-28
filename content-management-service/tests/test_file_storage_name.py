from shared.file_storage import storage_name

_FILE_ID = "6f1c7d4e-0000-4000-8000-00000000000a"


def test_storage_name_joins_the_extension() -> None:
    assert storage_name(_FILE_ID, "pdf") == f"{_FILE_ID}.pdf"


def test_storage_name_omits_the_dot_for_an_empty_extension() -> None:
    assert storage_name(_FILE_ID, "") == _FILE_ID
