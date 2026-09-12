import pytest
from srp_support import run_report, split_class, unit_named


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_constructor_initializing_every_field_does_not_hide_separate_groups(
    tmp_path, suffix
):
    source = split_class(suffix)
    if suffix == ".py":
        source += (
            "    def __init__(self, left, right):\n"
            "        self.left = left\n        self.right = right\n"
        )
    else:
        source = source[:-2] + (
            "constructor(left, right) {\nthis.left = left; this.right = right;\n}\n}\n"
        )
    owner = unit_named(run_report(tmp_path, source, suffix), "<module>.Worker")
    assert owner["metrics"]["supported_components"] == 2
    assert owner["coefficient"] < 0.8


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_short_internal_bridge_contributes_transitive_cohesion(tmp_path, suffix):
    source = split_class(suffix)
    if suffix == ".py":
        source += (
            "    def combine(self):\n        return self.task_0() + self.task_2()\n"
        )
    else:
        source = (
            source[:-2] + "combine() { return this.task_0() + this.task_2(); }\n}\n"
        )
    owner = unit_named(run_report(tmp_path, source, suffix), "<module>.Worker")

    assert owner["coefficient"] < 0.8
    assert owner["metrics"]["components"] == 1
    assert owner["metrics"]["loose_cohesion"] == 1
    assert owner["metrics"]["tight_cohesion"] < 1


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_static_field_access_counts_as_shared_state(tmp_path, suffix):
    source = split_class(suffix, cohesive=True)
    source = source.replace("self.left", "Worker.left").replace(
        "this.left", "Worker.left"
    )
    owner = unit_named(run_report(tmp_path, source, suffix), "<module>.Worker")

    assert owner["metrics"]["tight_cohesion"] == 1
    assert owner["coefficient"] == 0


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_separate_external_effects_are_detected_despite_shared_entity_state(
    tmp_path, suffix
):
    if suffix == ".py":
        source = "import httpx\nfrom pathlib import Path\nclass Worker:\n"
        for i, call in enumerate(
            ["httpx.get", "httpx.post", "Path('a').read_text", "Path('b').write_text"]
        ):
            source += (
                f"    def task_{i}(self):\n"
                + "        value = self.entity\n" * 5
                + f"        return {call}(value)\n"
            )
    else:
        source = 'import axios from "axios";\nimport * as fs from "node:fs";\nclass Worker {\n'
        for i, call in enumerate(
            ["axios.get", "axios.post", "fs.readFileSync", "fs.writeFileSync"]
        ):
            source += (
                f"task_{i}() {{\n"
                + "let value = this.entity;\n"
                + "value = this.entity;\n" * 4
                + f"return {call}(value);\n}}\n"
            )
        source += "}\n"
    report = run_report(tmp_path, source, suffix)
    owner = unit_named(report, "<module>.Worker")

    assert owner["metrics"]["tight_cohesion"] == 1
    assert owner["metrics"]["components"] == 1
    assert set(owner["metrics"]["effect_groups"]) == {"network", "filesystem"}
    assert 0.5 <= owner["coefficient"] < 0.8


def test_module_functions_can_form_independent_dependency_groups(tmp_path):
    source = "import httpx\nfrom pathlib import Path\n"
    for i, call in enumerate(
        ["httpx.get", "httpx.post", "Path('a').read_text", "Path('a').unlink"]
    ):
        source += (
            f"def task_{i}():\n    value = {call}()\n"
            "    result = str(value)\n    return result\n"
        )
    owner = unit_named(run_report(tmp_path, source), "<module>")

    assert 0 < owner["coefficient"] < 0.8
    assert owner["metrics"]["components"] == 2


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_module_state_remains_visible_after_resolving_module_bindings(tmp_path, suffix):
    source = (
        "left = []\nright = []\n"
        if suffix == ".py"
        else "const left = [], right = [];\n"
    )
    for index in range(4):
        state = "left" if index < 2 else "right"
        if suffix == ".py":
            source += (
                f"def task_{index}():\n    value = {state}.pop()\n"
                f"    {state}.append(value)\n    return value\n"
            )
        else:
            source += (
                f"function task_{index}() {{\n  const value = {state}.pop();\n"
                f"  {state}.push(value);\n  return value;\n}}\n"
            )
    report = run_report(tmp_path, source, suffix)
    owner = unit_named(report, "<module>")

    assert owner["metrics"]["supported_components"] == 2
    for index in range(4):
        unit = unit_named(report, f"<module>.task_{index}")
        assert unit["metrics"]["resources"] == [
            "global:left" if index < 2 else "global:right"
        ]
