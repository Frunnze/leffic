import pytest
from srp_support import CHECK, THRESHOLD, run_project, run_report, unit_named

EXTRACTION = "content-management-service/src/features/study_units_generation"


def worker_module(suffix, worlds):
    operations = {
        "network": ("httpx.get(name)", "axios.get(name)"),
        "filesystem": ("Path(name).read_text()", "fs.readFileSync(name)"),
        "process": ("subprocess.run([name])", "child_process.execSync(name)"),
    }
    if suffix == ".py":
        source = "import httpx\nimport subprocess\nfrom pathlib import Path\n\n\n"
        for index, world in enumerate(worlds):
            source += (
                f"def task_{index}(name):\n    return {operations[world][0]}\n\n\n"
            )
        return source
    source = 'import axios from "axios";\nimport * as fs from "node:fs";\n'
    source += 'import * as child_process from "node:child_process";\n\n'
    for index, world in enumerate(worlds):
        source += f"export function task_{index}(name) {{\n  return {operations[world][1]};\n}}\n\n"
    return source


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_a_module_with_one_outside_world_has_one_reason_to_change(tmp_path, suffix):
    report = run_report(tmp_path, worker_module(suffix, ["network", "network"]), suffix)
    owner = unit_named(report, "<module>")

    assert owner["entities"] == ["network"]
    assert not report["failed"]


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_a_module_reports_every_outside_world_and_the_member_reaching_it(
    tmp_path, suffix
):
    source = worker_module(suffix, ["network", "filesystem", "process"])
    owner = unit_named(run_report(tmp_path, source, suffix), "<module>")

    assert owner["entities"] == ["filesystem", "network", "process"]
    assert owner["coefficient"] >= THRESHOLD
    assert owner["entity_members"] == {
        "filesystem": ["<module>.task_1"],
        "network": ["<module>.task_0"],
        "process": ["<module>.task_2"],
    }


def test_every_separated_extraction_callable_keeps_one_reason_to_change(tmp_path):
    source_root = CHECK.parents[2] / EXTRACTION
    target = tmp_path / "src/features/study_units_generation"
    target.mkdir(parents=True)
    for name in ("youtube_transcript", "webpage_extractor", "text_sources"):
        (target / f"{name}.py").write_text((source_root / f"{name}.py").read_text())
    report = run_project(tmp_path)
    callables = [
        unit
        for file in report["files"]
        for unit in file["units"]
        if unit["kind"] == "callable"
    ]

    assert report["threshold"] == THRESHOLD
    assert max(len(unit["entities"]) for unit in callables) == 1


def test_a_module_gathering_two_single_entity_callables_still_blocks(tmp_path):
    source_root = CHECK.parents[2] / EXTRACTION
    target = tmp_path / "src/features/study_units_generation"
    target.mkdir(parents=True)
    for name in ("youtube_transcript", "webpage_extractor", "text_sources"):
        (target / f"{name}.py").write_text((source_root / f"{name}.py").read_text())
    report = run_project(tmp_path)
    owner = unit_named(report, "<module>")

    assert report["failed"]
    assert owner["entities"] == ["filesystem", "network"]
