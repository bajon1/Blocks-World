from collections.abc import Callable
from collections import Counter
from pathlib import Path

from .experiments import ExperimentRecord, load_problem_set, run_suite
from .problem import BlocksProblem, SearchResult, Variant


Solver = Callable[[BlocksProblem], SearchResult]
SolverLoader = Callable[[str, int, str | None], Solver]


def _validate_case_counts(
    basic_cases: list[tuple[str, BlocksProblem]],
    n8_cases: list[tuple[str, BlocksProblem]],
) -> None:
    basic_counts = Counter(len(problem.start) for _, problem in basic_cases)
    expected_basic = {n: 5 for n in range(3, 16)}
    if len(basic_cases) != 65 or dict(basic_counts) != expected_basic:
        raise ValueError(
            "Expected 65 base problems: exactly 5 for every N from 3 to 15"
        )

    if len(n8_cases) != 10 or any(
        len(problem.start) != 8 for _, problem in n8_cases
    ):
        raise ValueError("Expected exactly 10 N=8 comparison problems")


def run_standard_experiments(
    *,
    base_dir: str | Path,
    n8_dir: str | Path,
    solver_loader: SolverLoader,
    first_heuristic: str,
    second_heuristic: str,
    max_expanded: int = 1_000_000,
    on_record: Callable[[ExperimentRecord], None] | None = None,
) -> list[ExperimentRecord]:
    basic_cases = load_problem_set(base_dir, Variant.BASIC)
    n8_cases = load_problem_set(n8_dir, Variant.EXTENDED)
    _validate_case_counts(basic_cases, n8_cases)

    records: list[ExperimentRecord] = []
    records.extend(
        run_suite(
            basic_cases,
            "dfs",
            solver_loader("dfs", max_expanded, None),
            max_expanded=max_expanded,
            on_record=on_record,
        )
    )

    for algorithm in ("dfs", "bfs"):
        records.extend(
            run_suite(
                n8_cases,
                algorithm,
                solver_loader(algorithm, max_expanded, None),
                max_expanded=max_expanded,
                on_record=on_record,
            )
        )

    ida_cases = [
        case
        for case in load_problem_set(base_dir, Variant.EXTENDED)
        if len(case[1].start) in {6, 8, 10, 12, 15}
    ]
    for heuristic in (first_heuristic, second_heuristic):
        records.extend(
            run_suite(
                ida_cases,
                "ida_star",
                solver_loader("ida_star", max_expanded, heuristic),
                heuristic=heuristic,
                max_expanded=max_expanded,
                on_record=on_record,
            )
        )

    return records
