import json
from pathlib import Path

import pytest

from blocks_world.block_state import BlockState
from experiments.utils.experiments import (
    load_problem_set,
    run_suite,
    write_results,
)
from blocks_world.runner import run_experiment
from blocks_world.moves import Move
from blocks_world.io import write_problems
from blocks_world.problem import BlocksProblem, SearchResult, Variant


def test_run_experiment_records_verified_solver_result():
    problem = BlocksProblem(
        start=BlockState((0, 1, 0)),
        goal=BlockState((0, 0, 0)),
        variant=Variant.BASIC,
    )

    def solver(given_problem: BlocksProblem) -> SearchResult:
        assert given_problem == problem
        return SearchResult(
            moves=[Move(2, 0)],
            visited=12,
            is_solved=True,
        )

    record = run_experiment("n03-01", problem, "dfs", solver)

    assert record.case_id == "n03-01"
    assert record.status == "solved"
    assert record.move_count == 1
    assert record.expanded_nodes == 12
    assert record.elapsed_seconds >= 0
    assert record.verification == "passed"
    assert record.moves == ((2, 0),)


def test_run_experiment_reads_peak_states_from_solver_adapter():
    problem = BlocksProblem(
        start=BlockState((0, 0)),
        goal=BlockState((0, 0)),
        variant=Variant.BASIC,
    )

    class Solver:
        def __call__(self, _problem: BlocksProblem) -> SearchResult:
            return SearchResult(moves=[], visited=4, is_solved=True)

        def peak_stored_states(self) -> int:
            return 7

    record = run_experiment("measured", problem, "bfs", Solver())

    assert record.peak_stored_states == 7


def test_run_experiment_marks_unsolved_result_not_applicable():
    problem = BlocksProblem(
        start=BlockState((0, 0)),
        goal=BlockState((0, 1)),
        variant=Variant.EXTENDED,
    )

    def solver(_problem: BlocksProblem) -> SearchResult:
        return SearchResult(moves=[], visited=100, is_solved=False)

    record = run_experiment("limit", problem, "bfs", solver)

    assert record.status == "not_solved"
    assert record.move_count is None
    assert record.verification == "not_applicable"


def test_run_experiment_identifies_node_limit_without_changing_search_result():
    problem = BlocksProblem(
        start=BlockState((0, 0)),
        goal=BlockState((0, 1)),
        variant=Variant.EXTENDED,
    )

    def solver(_problem: BlocksProblem) -> SearchResult:
        return SearchResult(moves=[], visited=100, is_solved=False)

    record = run_experiment(
        "limit",
        problem,
        "bfs",
        solver,
        max_expanded=100,
    )

    assert record.status == "node_limit"


def test_run_experiment_marks_invalid_solution():
    problem = BlocksProblem(
        start=BlockState((0, 1)),
        goal=BlockState((0, 0)),
        variant=Variant.BASIC,
    )

    def solver(_problem: BlocksProblem) -> SearchResult:
        return SearchResult(moves=[], visited=1, is_solved=True)

    record = run_experiment("invalid", problem, "dfs", solver)

    assert record.status == "invalid_solution"
    assert record.verification.startswith("failed: Final state")


def test_write_results_serializes_records_as_json():
    problem = BlocksProblem(
        start=BlockState((0, 0)),
        goal=BlockState((0, 0)),
        variant=Variant.BASIC,
    )

    def solver(_problem: BlocksProblem) -> SearchResult:
        return SearchResult(moves=[], visited=1, is_solved=True)

    record = run_experiment("same", problem, "dfs", solver)
    path = Path("tests/_runtime_results.json")

    try:
        write_results(path, [record])
        payload = json.loads(path.read_text(encoding="utf-8"))

        assert payload[0]["case_id"] == "same"
        assert payload[0]["start"] == [0, 0]
        assert payload[0]["verification"] == "passed"
    finally:
        path.unlink(missing_ok=True)


def test_load_problem_set_and_run_suite():
    path = Path("tests/_runtime_problem_set.txt")
    try:
        write_problems(
            path,
            [
                BlocksProblem(
                    BlockState((0, 0, 0)),
                    BlockState(goal),
                    Variant.EXTENDED,
                )
                for goal in ((0, 1, 0), (0, 0, 2))
            ],
        )

        cases = load_problem_set(path, Variant.EXTENDED)
        assert len(cases) == 2
        assert cases[0][0] == "problem_n03_01"

        def solver(_problem: BlocksProblem) -> SearchResult:
            return SearchResult(moves=[], visited=25, is_solved=False)

        records = run_suite(cases, "dfs", solver)

        assert [record.case_id for record in records] == [
            "problem_n03_01",
            "problem_n03_02",
        ]
        assert all(record.expanded_nodes == 25 for record in records)
    finally:
        path.unlink(missing_ok=True)


def test_run_suite_reports_each_completed_record():
    problem = BlocksProblem(
        start=BlockState((0, 0)),
        goal=BlockState((0, 0)),
        variant=Variant.BASIC,
    )
    completed = []

    def solver(_problem: BlocksProblem) -> SearchResult:
        return SearchResult(moves=[], visited=0, is_solved=True)

    records = run_suite(
        [("first", problem), ("second", problem)],
        "bfs",
        solver,
        on_record=completed.append,
    )

    assert completed == records


def test_load_problem_set_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        load_problem_set("tests/does-not-exist", Variant.BASIC)
