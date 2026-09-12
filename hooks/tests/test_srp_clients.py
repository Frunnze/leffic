import pytest
from srp_support import (
    run_project,
    run_report,
    split_class,
    unit_named,
    write_split_project,
)


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_disconnected_groups_without_clients_are_review_only(tmp_path, suffix):
    owner = unit_named(
        run_report(tmp_path, split_class(suffix), suffix), "<module>.Worker"
    )

    assert 0 < owner["coefficient"] < 0.8
    assert owner["client_usage"]["components"]["status"] == "insufficient_evidence"
    assert owner["client_usage"]["components"]["similarity"] is None


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_shared_client_refutes_observed_segregation(tmp_path, suffix):
    write_split_project(tmp_path, suffix)
    before = unit_named(run_project(tmp_path), "<module>.Worker")
    source = (tmp_path / f"client_0_0{suffix}").read_text()
    source = source.replace("task_1", "task_2")
    (tmp_path / f"coordinator{suffix}").write_text(source)
    after = unit_named(run_project(tmp_path), "<module>.Worker")

    assert before["coefficient"] == 0.8
    assert after["coefficient"] < 0.8
    assert after["counterevidence"]
    assert after["client_usage"]["components"]["shared_clients"]


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_one_client_per_group_is_not_enough_to_block(tmp_path, suffix):
    write_split_project(tmp_path, suffix)
    for group in range(2):
        (tmp_path / f"client_{group}_1{suffix}").unlink()
    assert not run_project(tmp_path)["failed"]


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_different_methods_in_same_client_file_are_not_different_actors(
    tmp_path, suffix
):
    write_split_project(tmp_path, suffix)
    for i in range(2):
        path = tmp_path / f"client_0_{i}{suffix}"
        source = path.read_text()
        if suffix == ".py":
            source += "def another_use():\n    Worker().task_2()\n"
        else:
            source += "function anotherUse() { new Worker().task_2(); }\n"
        path.write_text(source)
    assert not run_project(tmp_path)["failed"]


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_internal_wrappers_inherit_observed_client_usage(tmp_path, suffix):
    source = split_class(suffix)
    if suffix == ".py":
        source += "    def wrapper(self):\n        return self.task_0()\n"
    else:
        source = source[:-2] + "wrapper() { return this.task_0(); }\n}\n"
    write_split_project(tmp_path, suffix, source)
    for i in range(2):
        path = tmp_path / f"client_0_{i}{suffix}"
        path.write_text(
            path.read_text().replace("task_0", "wrapper").replace("task_1", "wrapper")
        )
    owner = unit_named(run_project(tmp_path), "<module>.Worker")

    assert owner["client_usage"]["components"]["segregated"]
    assert owner["coefficient"] >= 0.8


@pytest.mark.parametrize("form", ["from .worker import Worker", "from . import worker"])
def test_python_relative_imports_resolve_inside_src_packages(tmp_path, form):
    root = tmp_path / "src" / "feature"
    write_split_project(root, ".py")
    for path in root.glob("client*.py"):
        source = path.read_text().replace("from worker import Worker", form)
        if form.endswith("worker"):
            source = source.replace(
                "worker = Worker()", "instance = worker.Worker()"
            ).replace("worker.task_", "instance.task_")
        path.write_text(source)
    assert run_project(tmp_path)["failed"]


def test_equal_module_names_in_different_services_do_not_share_clients(tmp_path):
    for service in ("one", "two"):
        write_split_project(tmp_path / service / "src", ".py")
    report = run_project(tmp_path)
    for file in report["files"]:
        if file["path"].endswith("worker.py"):
            owner = next(
                unit for unit in file["units"] if unit["name"] == "<module>.Worker"
            )
            groups = owner["client_usage"]["components"]["groups"]
            assert all(len(group) == 2 for group in groups)


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_top_level_shared_calls_prevent_false_segregation(tmp_path, suffix):
    write_split_project(tmp_path, suffix)
    source = (
        "from worker import Worker\nWorker().task_0()\nWorker().task_2()\n"
        if suffix == ".py"
        else 'import {Worker} from "./worker";\nnew Worker().task_0();\nnew Worker().task_2();\n'
    )
    (tmp_path / f"main{suffix}").write_text(source)

    assert not run_project(tmp_path)["failed"]


def test_typescript_compiler_resolves_ts_before_tsx(tmp_path):
    write_split_project(tmp_path, ".ts")
    (tmp_path / "worker.tsx").write_text((tmp_path / "worker.ts").read_text())

    report = run_project(tmp_path)
    assert report["failed"]
    for file in report["files"]:
        if file["path"].endswith("worker.tsx"):
            assert file["coefficient"] < 0.8


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_module_level_instances_preserve_client_populations(tmp_path, suffix):
    write_split_project(tmp_path, suffix)
    before = unit_named(run_project(tmp_path), "<module>.Worker")
    for path in tmp_path.glob("client*" + suffix):
        source = path.read_text()
        if suffix == ".py":
            source = source.replace(
                "def use():\n    worker = Worker()\n",
                "worker = Worker()\ndef use():\n",
            )
        else:
            source = source.replace(
                "function use() {\n  const worker = new Worker();\n",
                "const worker = new Worker();\nfunction use() {\n",
            )
        path.write_text(source)
    after = unit_named(run_project(tmp_path), "<module>.Worker")

    assert after["client_usage"] == before["client_usage"]
    assert after["coefficient"] == before["coefficient"] == 0.8
