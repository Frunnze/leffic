import pytest
from srp_support import run_project, run_report, unit_named, write_split_project


def computational_class(suffix, bridge=False):
    source = "class Worker:\n" if suffix == ".py" else "class Worker {\n"
    for index in range(4):
        if suffix == ".py":
            operation = (
                f"self.task_{index + 1}(value)" if index % 2 == 0 else "value * 2"
            )
            source += (
                f"    def task_{index}(self, value=1):\n"
                f"        result = {operation}\n"
                "        result += 1\n        return result\n"
            )
        else:
            operation = (
                f"this.task_{index + 1}(value)" if index % 2 == 0 else "value * 2"
            )
            source += (
                f"task_{index}(value=1) {{\nlet result = {operation};\n"
                "result += 1;\nreturn result;\n}\n"
            )
    if bridge:
        source += (
            "    def combine(self):\n        return self.task_0() + self.task_2()\n"
            if suffix == ".py"
            else "combine() { return this.task_0() + this.task_2(); }\n"
        )
    return source if suffix == ".py" else source + "}\n"


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_separate_pure_calculation_groups_with_separate_clients_block(tmp_path, suffix):
    write_split_project(tmp_path, suffix, computational_class(suffix))
    owner = unit_named(run_project(tmp_path), "<module>.Worker")

    assert owner["coefficient"] == 0.8
    assert owner["metrics"]["supported_components"] == 2
    assert owner["metrics"]["tight_cohesion"] is None
    assert owner["client_usage"]["components"]["segregated"]


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
@pytest.mark.parametrize(
    "counterexample", ["missing_clients", "shared_client", "bridge"]
)
def test_pure_calculations_need_independent_corroborating_clients(
    tmp_path, suffix, counterexample
):
    write_split_project(
        tmp_path, suffix, computational_class(suffix, counterexample == "bridge")
    )
    if counterexample == "missing_clients":
        for path in tmp_path.glob("client*"):
            path.unlink()
    elif counterexample == "shared_client":
        (tmp_path / f"shared{suffix}").write_text(
            (tmp_path / f"client_0_0{suffix}").read_text()
            + (tmp_path / f"client_1_0{suffix}").read_text().replace("use", "another")
        )
    assert not run_project(tmp_path)["failed"]


@pytest.mark.parametrize("suffix", [".py", ".ts"])
@pytest.mark.parametrize("spelling", ["task_", "delegate.task_"])
def test_bare_calls_and_calls_on_other_objects_are_not_internal_methods(
    tmp_path, suffix, spelling
):
    source = (
        computational_class(suffix)
        .replace("self.task_", spelling)
        .replace("this.task_", spelling)
    )
    write_split_project(tmp_path, suffix, source)
    owner = unit_named(run_project(tmp_path), "<module>.Worker")

    assert not owner["client_usage"]["components"]["segregated"]
    assert owner["metrics"]["supported_components"] == 0
    assert owner["coefficient"] < 0.8


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_callback_parameters_do_not_link_to_same_named_module_functions(
    tmp_path, suffix
):
    source = (
        "def helper(value):\n    return value\n"
        "def work(helper):\n    return helper(1)\n"
        if suffix == ".py"
        else "function helper(value) { return value; }\n"
        "function work(helper) { return helper(1); }\n"
    )
    unit = unit_named(run_report(tmp_path, source, suffix), "<module>.work")

    assert unit["metrics"]["links"] == []
