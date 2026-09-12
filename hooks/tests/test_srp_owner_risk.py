from pathlib import Path

import pytest
from srp_support import CHECK, run_project, run_report, unit_named


def complex_class(suffix, branches=6, foreign=7, cohesive=False, typed=False):
    source = "class Worker:\n" if suffix == ".py" else "class Worker {\n"
    for method in range(8):
        field = 0 if cohesive else method // 2
        if suffix == ".py":
            parameter = "data: Record" if typed else "data"
            source += f"    def task_{method}(self, {parameter}):\n        value = self.part_{field}\n"
            for item in range(foreign):
                source += f"        value += data.field_{item}\n"
            for item in range(branches):
                source += f"        if value > {item}:\n            value += 1\n"
            source += "        return value\n"
        else:
            parameter = "data: Record" if typed else "data"
            source += f"task_{method}({parameter}) {{\nlet value = this.part_{field};\n"
            for item in range(foreign):
                source += f"value += data.field_{item};\n"
            for item in range(branches):
                source += f"if (value > {item}) {{ value += 1; }}\n"
            source += "return value;\n}\n"
    if suffix != ".py":
        source += "}\n"
    if typed:
        source = (
            "from models import Record\n"
            if suffix == ".py"
            else 'import type {Record} from "./models";\n'
        ) + source
    return source


@pytest.mark.parametrize("suffix", [".py", ".ts"])
@pytest.mark.parametrize("typed", [False, True])
def test_god_class_requires_three_distinct_signals(tmp_path, suffix, typed):
    source = complex_class(suffix, typed=typed)
    owner = unit_named(run_report(tmp_path, source, suffix), "<module>.Worker")

    assert owner["god_class_risk"]
    assert owner["coefficient"] >= 0.8
    assert owner["metrics"]["weighted_methods"] == 56
    assert owner["metrics"]["foreign_data"] == 7
    assert owner["metrics"]["tight_cohesion"] < 1 / 3


@pytest.mark.parametrize("suffix", [".py", ".ts"])
@pytest.mark.parametrize(
    "changes", [{"branches": 1}, {"foreign": 5}, {"cohesive": True}]
)
def test_removing_any_god_class_signal_prevents_a_block(tmp_path, suffix, changes):
    owner = unit_named(
        run_report(tmp_path, complex_class(suffix, **changes), suffix),
        "<module>.Worker",
    )

    assert not owner["god_class_risk"]
    assert owner["coefficient"] < 0.8


@pytest.mark.parametrize("name", ["link_extractor", "renamed_adapter"])
def test_combined_link_adapters_block_at_stricter_threshold(tmp_path, name):
    source_root = (
        CHECK.parents[2]
        / "content-management-service/src/features/study_units_generation"
    )
    target = tmp_path / "src/features/study_units_generation"
    target.mkdir(parents=True)
    (target / f"{name}.py").write_text(
        (source_root / "youtube_transcript.py").read_text()
        + "\n"
        + (source_root / "webpage_extractor.py").read_text()
    )
    caller = (
        (source_root / "text_sources.py")
        .read_text()
        .replace(".youtube_transcript import", f".{name} import")
        .replace(".webpage_extractor import", f".{name} import")
    )
    (target / "text_sources.py").write_text(caller)
    report = run_project(tmp_path)
    file = next(
        file for file in report["files"] if Path(file["path"]).name == f"{name}.py"
    )
    owner = next(unit for unit in file["units"] if unit["name"] == "<module>")

    assert report["threshold"] == 0.5
    assert report["failed"]
    assert 0.5 <= owner["coefficient"] < 0.8
    assert owner["metrics"]["supported_components"] >= 2
    assert owner["counterevidence"] == ["observed callers use multiple groups together"]
    assert owner["client_usage"]["components"]["shared_clients"] == [
        str(target / "text_sources.py")
    ]


def test_separate_link_adapters_pass_the_stricter_gate(tmp_path):
    source_root = (
        CHECK.parents[2]
        / "content-management-service/src/features/study_units_generation"
    )
    target = tmp_path / "src/features/study_units_generation"
    target.mkdir(parents=True)
    for name in ("youtube_transcript", "webpage_extractor", "text_sources"):
        (target / f"{name}.py").write_text((source_root / f"{name}.py").read_text())
    report = run_project(tmp_path)

    assert report["threshold"] == 0.5
    assert report["coefficient"] < 0.5
    assert not report["failed"]
