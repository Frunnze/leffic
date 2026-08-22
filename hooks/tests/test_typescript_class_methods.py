from pathlib import Path

from typescript_finder_support import CHECKS, report_from

_FINDER = CHECKS / "class-methods" / "class_method_counts.js"
_MODULE = "src/shared/api/http.ts"


def _report_for(tmp_path: Path, source: str) -> list[str]:
    return report_from(_FINDER, tmp_path, {_MODULE: source})


def _class_with(members: str) -> str:
    return f"export class Crowded {{\n{members}}}\n"


def _instance_methods(count: int) -> str:
    written = ""

    for number in range(count):
        body = f"    return {number};"
        written += f"  method{number}(): number {{\n{body}\n  }}\n"

    return written


def _static_methods(count: int) -> str:
    return _instance_methods(count).replace("  method", "  static method")


def test_flags_a_class_with_five_instance_methods(tmp_path: Path) -> None:
    report = _report_for(tmp_path, _class_with(_instance_methods(5)))

    assert report == [f"{_MODULE}:1: Crowded has 5 methods"]


def test_allows_a_class_with_four_instance_methods(tmp_path: Path) -> None:
    assert _report_for(tmp_path, _class_with(_instance_methods(4))) == []


def test_allows_a_class_of_statics_because_it_is_a_module(
    tmp_path: Path,
) -> None:
    assert _report_for(tmp_path, _class_with(_static_methods(9))) == []


def test_counts_the_constructor_as_a_method(tmp_path: Path) -> None:
    members = "  constructor() {\n    this.value = 1;\n  }\n"
    members += "  value = 0;\n"
    report = _report_for(
        tmp_path, _class_with(members + _instance_methods(4))
    )

    assert report == [f"{_MODULE}:1: Crowded has 5 methods"]


def test_counts_an_accessor_as_a_method(tmp_path: Path) -> None:
    members = "  get value(): number {\n    return 1;\n  }\n"
    report = _report_for(
        tmp_path, _class_with(members + _instance_methods(4))
    )

    assert report == [f"{_MODULE}:1: Crowded has 5 methods"]


def test_ignores_fields_that_hold_arrow_functions(tmp_path: Path) -> None:
    members = ""

    for number in range(9):
        members += f"  field{number} = (): number => {number};\n"

    assert _report_for(tmp_path, _class_with(members)) == []
