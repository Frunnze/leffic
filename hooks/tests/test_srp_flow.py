import pytest
from srp_support import mixed_function, run_report, unit_named


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_independent_effects_have_substantial_disjoint_slices(tmp_path, suffix):
    unit = unit_named(
        run_report(tmp_path, mixed_function(suffix), suffix), "<module>.work"
    )

    assert unit["coefficient"] >= 0.8
    assert unit["effect_flow"]["independent_effects"]
    assert unit["effect_flow"]["pairs"] == [
        {"left": "filesystem", "right": "network", "overlap": 0, "data_flow": False}
    ]


@pytest.mark.parametrize("suffix", [".py", ".ts", ".tsx"])
def test_network_results_written_to_disk_are_one_workflow(tmp_path, suffix):
    source = mixed_function(suffix)
    if suffix == ".py":
        source = source.replace(
            "    httpx.get(address)", "    response = httpx.get(address)"
        )
        source = source.replace("write_text('x')", "write_text(response.text)")
    else:
        source = source.replace(
            "  axios.get(address)", "  const response = await axios.get(address)"
        )
        source = source.replace(
            'writeFileSync(filename, "x")', "writeFileSync(filename, response.data)"
        )
    unit = unit_named(run_report(tmp_path, source, suffix), "<module>.work")

    assert unit["coefficient"] < 0.8
    assert unit["effect_flow"]["shared_workflow"]
    assert unit["effect_flow"]["pairs"][0]["data_flow"]
    assert unit["counterevidence"]


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_shared_computation_is_counterevidence_even_without_io_chaining(
    tmp_path, suffix
):
    source = mixed_function(suffix).replace("Path(filename)", "Path(address)")
    source = source.replace("Sync(filename", "Sync(address")
    unit = unit_named(run_report(tmp_path, source, suffix), "<module>.work")

    assert unit["coefficient"] < 0.8
    assert unit["effect_flow"]["pairs"][0]["overlap"] >= 0.5


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_unrelated_padding_cannot_turn_trivial_effects_into_independent_jobs(
    tmp_path, suffix
):
    source = mixed_function(suffix).replace("get(address)", "get('url')")
    source = source.replace("post(address)", "post('url')")
    source = source.replace("Path(filename)", "Path('a')")
    source = source.replace("Sync(filename", "Sync('a'")
    unit = unit_named(run_report(tmp_path, source, suffix), "<module>.work")

    assert unit["coefficient"] < 0.8
    assert unit["effect_flow"]["status"] == "insufficient_evidence"


@pytest.mark.parametrize("suffix", [".py", ".ts"])
def test_variable_renaming_does_not_change_workflow_evidence(tmp_path, suffix):
    source = mixed_function(suffix)
    original = run_report(tmp_path, source, suffix)
    renamed = run_report(
        tmp_path,
        source.replace("value_", "datum_").replace("address", "destination"),
        suffix,
    )

    assert original["coefficient"] == renamed["coefficient"]
    assert (
        unit_named(original, "<module>.work")["effect_flow"]
        == unit_named(renamed, "<module>.work")["effect_flow"]
    )
