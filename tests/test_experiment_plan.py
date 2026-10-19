import pytest
from pathlib import Path
import shutil

from blocks_world.block_state import BlockState
from blocks_world.experiment_plan import run_standard_experiments
from blocks_world.generator import generate_dataset
from blocks_world.io import write_problem
from blocks_world.problem import BlocksProblem, SearchResult, Variant


@pytest.fixture
def standard_dataset():
    root = Path("tests/_runtime_standard_dataset")
    base_dir = root / "base"
    n8_dir = root / "n8_extended"
    shutil.rmtree(root, ignore_errors=True)
    generate_dataset(base_dir, 42, 5, 3, 15, Variant.BASIC)
    generate_dataset(n8_dir, 42, 10, 8, 8, Variant.EXTENDED)
    yield base_dir, n8_dir
    shutil.rmtree(root, ignore_errors=True)


def test_standard_experiment_plan_covers_all_required_cases(standard_dataset):
    base_dir, n8_dir = standard_dataset
    loader_calls = []
    completed = []

    def solver_loader(algorithm, max_expanded, heuristic):
        loader_calls.append((algorithm, max_expanded, heuristic))

        class Solver:
            def __call__(self, _problem):
                return SearchResult(moves=[], visited=1, is_solved=False)

            def peak_stored_states(self):
                return 7

        return Solver()

    records = run_standard_experiments(
        base_dir=base_dir,
        n8_dir=n8_dir,
        solver_loader=solver_loader,
        first_heuristic="misplaced_supports",
        second_heuristic="improved",
        max_expanded=123,
        on_record=completed.append,
    )

    assert len(records) == 135
    assert sum(
        record.algorithm == "dfs" and record.variant == "basic"
        for record in records
    ) == 65
    assert sum(
        record.algorithm in {"dfs", "bfs"}
        and record.variant == "extended"
        and record.n == 8
        and record.heuristic is None
        for record in records
    ) == 20
    assert sum(record.algorithm == "ida_star" for record in records) == 50
    assert all(record.peak_stored_states == 7 for record in records)
    assert loader_calls == [
        ("dfs", 123, None),
        ("dfs", 123, None),
        ("bfs", 123, None),
        ("ida_star", 123, "misplaced_supports"),
        ("ida_star", 123, "improved"),
    ]
    assert completed == records


def test_standard_experiment_plan_rejects_incomplete_dataset():
    root = Path("tests/_runtime_incomplete_dataset")
    base_dir = root / "base"
    n8_dir = root / "n8"
    root.mkdir(exist_ok=True)
    base_dir.mkdir()
    n8_dir.mkdir()
    state = BlockState((0, 0, 0))
    problem_path = base_dir / "problem_n03_01.txt"
    try:
        write_problem(
            problem_path,
            BlocksProblem(state, BlockState((0, 1, 0)), Variant.BASIC),
        )

        with pytest.raises(ValueError, match="65 base problems"):
            run_standard_experiments(
                base_dir=base_dir,
                n8_dir=n8_dir,
                solver_loader=lambda *_: None,
                first_heuristic="misplaced_supports",
                second_heuristic="misplaced_supports_with_blockers",
            )
    finally:
        problem_path.unlink(missing_ok=True)
        base_dir.rmdir()
        n8_dir.rmdir()
        root.rmdir()
