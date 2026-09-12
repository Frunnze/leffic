from dataclasses import replace
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st
from srp_support import (
    THRESHOLD,
    CallableFacts,
    callable_score,
    mixed_function,
    owner_score,
    run_project,
    run_report,
    split_class,
    unit_named,
    write_split_project,
)


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_independent_state_groups_reach_high_confidence(tmp_path, suffix):
    write_split_project(tmp_path, suffix)
    report = run_project(tmp_path)
    owner = unit_named(report, "<module>.Worker")

    assert owner["coefficient"] == 0.8
    assert report["failed"]
    assert owner["metrics"]["components"] == 2
    assert owner["metrics"]["supported_components"] == 2
    assert owner["metrics"]["tight_cohesion"] == pytest.approx(1 / 3)


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_shared_state_keeps_a_focused_class_below_threshold(tmp_path, suffix):
    report = run_report(tmp_path, split_class(suffix, cohesive=True), suffix)

    assert not report["failed"]
    assert unit_named(report, "<module>.Worker")["coefficient"] == 0


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_long_complex_mixed_io_function_fails(tmp_path, suffix):
    report = run_report(tmp_path, mixed_function(suffix), suffix)
    unit = unit_named(report, "<module>.work")

    assert report["failed"]
    assert unit["coefficient"] > THRESHOLD
    assert set(unit["effect_domains"]) == {"network", "filesystem"}


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_stricter_gate_includes_moderate_single_concern_scores(tmp_path, suffix):
    report = run_report(tmp_path, mixed_function(suffix, mixed=False), suffix)

    assert THRESHOLD <= report["coefficient"] < 0.8
    assert report["failed"]


def test_stricter_gate_includes_moderate_orchestration_scores(tmp_path):
    source = (
        "import httpx\nfrom pathlib import Path\ndef export():\n"
        "    first = httpx.get('one')\n    second = httpx.post('two')\n"
        "    Path('one').write_text(first.text)\n"
        "    return Path('two').read_text() + second.text\n"
    )
    report = run_report(tmp_path, source)

    assert THRESHOLD <= report["coefficient"] < 0.8
    assert report["failed"]


@given(st.integers(0, 10000), st.integers(0, 1000), st.integers(0, 100))
def test_scores_are_bounded_and_size_alone_cannot_block(lines, branches, params):
    facts = CallableFacts(
        "f",
        1,
        "module",
        lines=lines,
        statements=lines,
        complexity=branches,
        nesting=branches,
        parameters=params,
        locals=params,
    )
    score = callable_score(facts)["coefficient"]
    mixed = replace(
        facts,
        calls=[
            "httpx.get",
            "httpx.post",
            "pathlib.Path.read_text",
            "pathlib.Path.unlink",
        ],
    )

    assert 0 <= score < THRESHOLD
    assert 0 <= callable_score(mixed)["coefficient"] <= 1


def test_zero_and_maximal_evidence_endpoints():
    assert callable_score(CallableFacts("f", 1, "m"))["coefficient"] == 0
    facts = CallableFacts(
        "f",
        1,
        "m",
        lines=100,
        statements=100,
        complexity=20,
        nesting=8,
        parameters=10,
        locals=20,
        calls=[
            "httpx.get",
            "httpx.post",
            "pathlib.Path.unlink",
            "pathlib.Path.read_text",
        ]
        + [f"f{i}" for i in range(12)],
        flow=[
            {
                "line": i + 1,
                "reads": [f"v{i - 1}"] if i % 4 else [],
                "writes": [f"v{i}"],
                "compound": False,
                "calls": calls,
            }
            for i, calls in enumerate(
                [
                    [],
                    [],
                    ["httpx.get"],
                    ["httpx.post"],
                    [],
                    [],
                    ["pathlib.Path.read_text"],
                    ["pathlib.Path.unlink"],
                ]
            )
        ],
    )
    assert callable_score(facts)["coefficient"] == 1


@given(st.integers(0, 1000))
def test_increasing_method_size_does_not_reduce_its_score(lines):
    facts = CallableFacts(
        "f",
        1,
        "m",
        lines=lines,
        statements=40,
        complexity=12,
        nesting=4,
        calls=["httpx.get", "httpx.post", "fs.readFile", "fs.writeFile"],
    )
    larger = replace(facts, lines=lines + 10)

    assert callable_score(larger)["coefficient"] >= callable_score(facts)["coefficient"]


def test_empty_owner_exposes_unmeasurable_cohesion():
    report = owner_score({"name": "m", "kind": "module", "line": 1}, [])

    assert report["coefficient"] == 0
    assert report["metrics"]["tight_cohesion"] is None
    assert report["metrics"]["normalized_components"] is None


def test_methods_without_shared_resources_are_not_sufficient_evidence(tmp_path: Path):
    source = "\n".join(
        f"def utility_{i}(value):\n    result = value + {i}\n    return result\n"
        for i in range(10)
    )
    assert not run_report(tmp_path, source)["failed"]
