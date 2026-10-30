import json
from pathlib import Path

import pytest


NOTEBOOK = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "experiment_4_4.ipynb"
)


def execute_notebook_cells() -> dict[str, object]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {"__name__": "__report_test__"}
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        exec(compile(source, f"notebook-cell-{index}", "exec"), namespace)
    return namespace


def test_report_contains_no_mojibake():
    notebook_text = NOTEBOOK.read_text(encoding="utf-8")

    assert not any(marker in notebook_text for marker in ("Ã", "Ä", "Å", "â"))


def test_report_executes_against_complete_results():
    namespace = execute_notebook_cells()

    assert len(namespace["records"]) == 135
    assert len(namespace["dfs_basic"]) == 65
    assert len(namespace["comparison"]) == 20
    assert len(namespace["ida"]) == 50


def test_report_rejects_missing_results(monkeypatch):
    missing_root = Path("tests/_runtime_missing_report")
    missing_root.mkdir(exist_ok=True)
    monkeypatch.chdir(missing_root)

    try:
        with pytest.raises(AssertionError, match="results.json"):
            execute_notebook_cells()
    finally:
        monkeypatch.undo()
        missing_root.rmdir()
