from pathlib import Path

from property_coverage_support import given_test, missing, report_for


def test_flags_a_route_handler(tmp_path: Path) -> None:
    source = "@router.get('/due')\nasync def list_due():\n    ...\n"

    assert report_for(tmp_path, source, "") == [missing("list_due", 2)]


def test_accepts_an_async_function_with_a_property_test(
    tmp_path: Path,
) -> None:
    tests = given_test("test_list_due_property_returns_only_due_cards")
    source = "async def list_due():\n    ...\n"

    assert report_for(tmp_path, source, tests) == []


def test_rejects_a_test_without_the_given_decorator(tmp_path: Path) -> None:
    tests = "def test_next_review_property_is_stable():\n    pass\n"
    report = report_for(tmp_path, "def next_review():\n    ...\n", tests)

    assert report == [missing("next_review", 1)]


def test_accepts_given_beneath_a_settings_decorator(tmp_path: Path) -> None:
    tests = given_test(
        "test_next_review_property_is_stable",
        "@settings(max_examples=10)\n@given()",
    )

    assert report_for(tmp_path, "def next_review():\n    ...\n", tests) == []


def test_accepts_a_qualified_hypothesis_given(tmp_path: Path) -> None:
    tests = (
        "import hypothesis\n"
        "@hypothesis.given()\n"
        "def test_next_review_property_is_stable():\n"
        "    pass\n"
    )

    assert report_for(tmp_path, "def next_review():\n    ...\n", tests) == []
