from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import asdict
import json
from pathlib import Path

from blocks_world.io import read_problems
from blocks_world.problem import BlocksProblem, SearchResult, Variant
from blocks_world.runner import ExperimentRecord, run_experiment


Solver = Callable[[BlocksProblem], SearchResult]
SolverLoader = Callable[[str, int, str | None], Solver]


def load_problem_set(
    path: str | Path,
    variant: Variant,
) -> list[tuple[str, BlocksProblem]]:
    problems = read_problems(path, variant)
    counts: Counter[int] = Counter()
    cases = []
    for problem in problems:
        n = len(problem.start)
        counts[n] += 1
        cases.append((f"problem_n{n:02d}_{counts[n]:02d}", problem))
    return cases


def run_suite(
    cases: Iterable[tuple[str, BlocksProblem]],
    algorithm: str,
    solver: Callable[[BlocksProblem], SearchResult],
    *,
    heuristic: str | None = None,
    max_expanded: int | None = None,
    on_record: Callable[[ExperimentRecord], None] | None = None,
) -> list[ExperimentRecord]:
    records = []
    for case_id, problem in cases:
        record = run_experiment(
            case_id,
            problem,
            algorithm,
            solver,
            heuristic=heuristic,
            max_expanded=max_expanded,
        )
        records.append(record)
        if on_record is not None:
            on_record(record)
    return records


def write_results(
    path: str | Path,
    records: Iterable[ExperimentRecord],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(record) for record in records]
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    temporary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


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
