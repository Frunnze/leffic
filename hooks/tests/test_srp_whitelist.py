import json
import subprocess
import sys

import pytest
from check_support import link_real_python, repository, run_check
from srp_support import CHECK, mixed_function, split_class, unit_named


def review_class():
    return split_class().replace(
        "return value", "result = str(value)\n        return result"
    )


def exception(path="worker.py", **changes):
    return {
        "path": path,
        "kind": "class",
        "name": "<module>.Worker",
        "reason": "Synthetic reviewed adapter with one reason to change.",
        **changes,
    }


def scan(root, entries):
    whitelist = root / "whitelist.txt"
    whitelist.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n")
    return subprocess.run(
        [
            sys.executable,
            str(CHECK / "srp_check.py"),
            "--json",
            "--whitelist",
            str(whitelist),
            str(root),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("spelling", ["relative", "absolute", "symlink"])
def test_whitelist_exempts_only_the_reviewed_unit_and_preserves_its_evidence(
    tmp_path, spelling
):
    source = tmp_path / "source with spaces.py"
    source.write_text(review_class())
    path = source.name if spelling == "relative" else str(source)
    if spelling == "symlink":
        alias = tmp_path / "alias.py"
        alias.symlink_to(source)
        path = str(alias)
    result = scan(tmp_path, [exception(path)])
    report = json.loads(result.stdout)
    unit = unit_named(report, "<module>.Worker")

    assert result.returncode == 0, result.stderr
    assert report["coefficient"] < 0.5
    assert report["raw_coefficient"] == 0.5
    assert report["whitelisted_count"] == 1
    assert len(report["files"]) == 1
    assert report["files"][0]["raw_coefficient"] == 0.5
    assert unit["coefficient"] == 0.5
    assert unit["whitelisted"]
    assert unit["whitelist_reason"] == exception()["reason"]
    assert unit["reasons"]


@pytest.mark.parametrize("location", ["same_file", "other_file"])
def test_whitelist_does_not_suppress_other_findings(tmp_path, location):
    source = tmp_path / "worker.py"
    source.write_text(review_class())
    if location == "same_file":
        source.write_text(source.read_text() + "\n" + mixed_function())
    else:
        (tmp_path / "another.py").write_text(review_class())
    result = scan(tmp_path, [exception()])
    report = json.loads(result.stdout)

    assert result.returncode == 1
    assert report["failed"]
    assert report["coefficient"] >= 0.5
    assert report["whitelisted_count"] == 1
    assert any(
        unit["coefficient"] >= 0.5 and not unit["whitelisted"]
        for file in report["files"]
        for unit in file["units"]
    )


@pytest.mark.parametrize(
    "changes", [{"path": "*.py"}, {"name": "*"}, {"kind": "module"}]
)
def test_whitelist_matches_exact_path_kind_and_name(tmp_path, changes):
    (tmp_path / "worker.py").write_text(review_class())
    result = scan(tmp_path, [exception(**changes)])
    report = json.loads(result.stdout)

    assert result.returncode == 1
    assert report["whitelisted_count"] == 0


@pytest.mark.parametrize(
    "problem",
    ["missing_reason", "empty_reason", "nonstring", "kind", "extra", "duplicate"],
)
def test_invalid_whitelists_are_analysis_errors(tmp_path, problem):
    (tmp_path / "worker.py").write_text(review_class())
    entry = exception()
    if problem == "missing_reason":
        del entry["reason"]
    elif problem == "empty_reason":
        entry["reason"] = "  "
    elif problem == "nonstring":
        entry["name"] = ["<module>.Worker"]
    elif problem == "kind":
        entry["kind"] = "file"
    elif problem == "extra":
        entry["anything"] = "typo"
    result = scan(tmp_path, [entry, entry] if problem == "duplicate" else [entry])

    assert result.returncode == 2
    assert "invalid SRP whitelist" in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("contents", [None, "{broken json}\n"])
def test_missing_or_malformed_whitelist_cannot_pass(tmp_path, contents):
    whitelist = tmp_path / "whitelist.txt"
    if contents is not None:
        whitelist.write_text(contents)
    result = subprocess.run(
        [
            sys.executable,
            str(CHECK / "srp_check.py"),
            "--json",
            "--whitelist",
            str(whitelist),
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "SRP analysis error" in result.stderr
    assert result.stdout == ""


def test_hook_reads_adjacent_whitelist_and_instructs_the_agent(tmp_path):
    repository(tmp_path)
    link_real_python(tmp_path)
    source = tmp_path / "user-service/src/worker.py"
    source.parent.mkdir(parents=True)
    source.write_text(review_class())
    whitelist = tmp_path / "hooks/checks/single-responsibility/whitelist.txt"
    whitelist.write_text(
        "# Reviewed exception\n\n"
        + json.dumps(exception("user-service/src/worker.py"))
        + "\n"
    )
    result = run_check(tmp_path, "single-responsibility")

    assert result.returncode == 0, result.stderr
    assert "whitelisted=1" in result.stdout
    assert (
        "Agent: first identify whether each finding is a real SRP violation"
        in result.stdout
    )
    assert "Fix only the real violations" in result.stdout
    assert "never refactor it" in result.stdout
    assert "hooks/checks/single-responsibility/whitelist.txt" in result.stdout
