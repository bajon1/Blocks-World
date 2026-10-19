from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from time import perf_counter

from .io import read_problem
from .problem import BlocksProblem, SearchResult, Variant
from .verifier import SolutionVerificationError, verify_solution


@dataclass(frozen=True, slots=True)
class ExperimentRecord:
    case_id: str
    n: int
    variant: str
    algorithm: str
    heuristic: str | None
    start: tuple[int, ...]
    goal: tuple[int, ...]
    status: str
    moves: tuple[tuple[int, int], ...]
    move_count: int | None
    expanded_nodes: int
    peak_stored_states: int | None
    elapsed_seconds: float
    verification: str


def load_problem_set(
    directory: str | Path,
    variant: Variant,
) -> list[tuple[str, BlocksProblem]]:
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Problem directory does not exist: {directory}")

    return [
        (path.stem, read_problem(path, variant))
        for path in sorted(directory.glob("problem_*.txt"))
    ]


def run_experiment(
    case_id: str,
    problem: BlocksProblem,
    algorithm: str,
    solver: Callable[[BlocksProblem], SearchResult],
    *,
    heuristic: str | None = None,
    peak_stored_states: int | None = None,
    max_expanded: int | None = None,
) -> ExperimentRecord:
    started = perf_counter()
    result = solver(problem)
    elapsed_seconds = perf_counter() - started

    if peak_stored_states is None:
        peak_provider = getattr(solver, "peak_stored_states", None)
        if callable(peak_provider):
            peak_stored_states = peak_provider()

    if result.is_solved:
        status = "solved"
        move_count: int | None = result.n_moves
        try:
            verify_solution(problem, result)
            verification = "passed"
        except SolutionVerificationError as error:
            status = "invalid_solution"
            verification = f"failed: {error}"
    else:
        status = (
            "node_limit"
            if max_expanded is not None and result.visited >= max_expanded
            else "not_solved"
        )
        move_count = None
        verification = "not_applicable"

    return ExperimentRecord(
        case_id=case_id,
        n=len(problem.start),
        variant=problem.variant.value,
        algorithm=algorithm,
        heuristic=heuristic,
        start=problem.start.state,
        goal=problem.goal.state,
        status=status,
        moves=tuple(tuple(move) for move in result.moves),
        move_count=move_count,
        expanded_nodes=result.visited,
        peak_stored_states=peak_stored_states,
        elapsed_seconds=elapsed_seconds,
        verification=verification,
    )


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
