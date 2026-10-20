from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter

from .problem import BlocksProblem, SearchResult
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
