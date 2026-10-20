import pytest
from pathlib import Path

from blocks_world.block_state import BlockState
from experiments.utils.experiments import run_standard_experiments
from blocks_world.generator import generate_dataset
from blocks_world.io import write_problems
from blocks_world.problem import BlocksProblem, SearchResult, Variant


@pytest.fixture
def standard_dataset():
    root = Path("tests/_runtime_standard_dataset")
    base_dir = root / "base.txt"
    n8_dir = root / "n8_extended.txt"
    root.mkdir(exist_ok=True)
    generate_dataset(base_dir, 42, 5, 3, 15, Variant.BASIC)
    generate_dataset(n8_dir, 42, 10, 8, 8, Variant.EXTENDED)
    yield base_dir, n8_dir
    base_dir.unlink(missing_ok=True)
    n8_dir.unlink(missing_ok=True)
    root.rmdir()


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
        first_heuristic="misplaced",
        second_heuristic="foundation",
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
        ("ida_star", 123, "misplaced"),
        ("ida_star", 123, "foundation"),
    ]
    assert completed == records


def test_standard_experiment_plan_rejects_incomplete_dataset():
    root = Path("tests/_runtime_incomplete_dataset")
    base_dir = root / "base.txt"
    n8_dir = root / "n8.txt"
    root.mkdir(exist_ok=True)
    state = BlockState((0, 0, 0))
    try:
        write_problems(
            base_dir,
            [BlocksProblem(state, BlockState((0, 1, 0)), Variant.BASIC)],
        )
        n8_state = BlockState((0,) * 8)
        write_problems(
            n8_dir,
            [
                BlocksProblem(
                    n8_state,
                    BlockState((0, 1, 0, 0, 0, 0, 0, 0)),
                    Variant.EXTENDED,
                )
            ],
        )

        with pytest.raises(ValueError, match="65 base problems"):
            run_standard_experiments(
                base_dir=base_dir,
                n8_dir=n8_dir,
                solver_loader=lambda *_: None,
                first_heuristic="misplaced",
                second_heuristic="foundation",
            )
    finally:
        base_dir.unlink(missing_ok=True)
        n8_dir.unlink(missing_ok=True)
        root.rmdir()
