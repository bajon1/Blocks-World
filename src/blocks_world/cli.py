import argparse
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
import sys
from typing import Sequence

from .generator import generate_dataset
from .io import read_problem
from .problem import BlocksProblem, SearchResult, Variant
from .runner import run_experiment


Solver = Callable[[BlocksProblem], SearchResult]
SolverLoader = Callable[[str, int, str | None], Solver]


def load_solver(
    algorithm: str,
    max_expanded: int,
    heuristic: str | None,
) -> Solver:
    locations = {
        "dfs": ("blocks_world.solvers.dfs", "dfs"),
        "bfs": ("blocks_world.solvers.bfs", "bfs"),
        "ida_star": ("blocks_world.solvers.idastar", "ida_star"),
    }
    module_name, function_name = locations[algorithm]

    try:
        module = import_module(module_name)
        function = getattr(module, function_name)
    except (ModuleNotFoundError, AttributeError) as error:
        raise ValueError(f"Solver {algorithm!r} is not available") from error

    def configured(problem: BlocksProblem) -> SearchResult:
        options: dict[str, object] = {"max_expanded": max_expanded}
        if algorithm == "ida_star":
            options["heuristic"] = heuristic
        return function(problem, **options)

    peak_provider = getattr(module, "get_peak_stored_states", None)
    if callable(peak_provider):
        configured.peak_stored_states = peak_provider

    return configured


def problem_main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read a Blocks World problem")
    parser.add_argument("path", type=Path)
    parser.add_argument("variant", choices=[variant.value for variant in Variant])
    args = parser.parse_args(argv)

    print(read_problem(args.path, Variant(args.variant)))
    return 0


def generate_main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate reproducible Blocks World problems"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--min-blocks", type=int, default=3)
    parser.add_argument("--max-blocks", type=int, default=15)
    parser.add_argument(
        "--variant",
        choices=[variant.value for variant in Variant],
        default=Variant.BASIC.value,
    )
    args = parser.parse_args(argv)

    if args.count < 1:
        parser.error("count must be positive")
    if args.min_blocks < 3:
        parser.error("min-blocks must be at least 3")
    if args.max_blocks < args.min_blocks:
        parser.error("max-blocks must not be smaller than min-blocks")

    output = args.output or Path("data/generated") / f"seed_{args.seed}.txt"
    problems = generate_dataset(
        output_path=output,
        seed=args.seed,
        count_per_n=args.count,
        min_blocks=args.min_blocks,
        max_blocks=args.max_blocks,
        variant=Variant(args.variant),
    )

    print(f"Generated {len(problems)} problems")
    print(f"Saved to: {output}")
    return 0


def solve_main(
    argv: Sequence[str] | None = None,
    *,
    solver_loader: SolverLoader = load_solver,
) -> int:
    parser = argparse.ArgumentParser(description="Solve a Blocks World problem")
    parser.add_argument("path", type=Path)
    parser.add_argument("variant", choices=[variant.value for variant in Variant])
    parser.add_argument("algorithm", choices=("dfs", "bfs", "ida_star"))
    parser.add_argument("--heuristic")
    parser.add_argument("--max-expanded", type=int, default=1_000_000)
    args = parser.parse_args(argv)

    if args.max_expanded < 1:
        parser.error("max-expanded must be positive")
    if args.algorithm == "ida_star" and not args.heuristic:
        parser.error("ida_star requires --heuristic")

    try:
        problem = read_problem(args.path, Variant(args.variant))
        solver = solver_loader(
            args.algorithm,
            args.max_expanded,
            args.heuristic,
        )
        record = run_experiment(
            args.path.stem,
            problem,
            args.algorithm,
            solver,
            heuristic=args.heuristic,
            max_expanded=args.max_expanded,
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"status: {record.status}")
    print(f"moves: {list(record.moves)}")
    print(f"length: {record.move_count}")
    print(f"expanded nodes: {record.expanded_nodes}")
    print(f"peak stored states: {record.peak_stored_states}")
    print(f"elapsed seconds: {record.elapsed_seconds:.6f}")
    print(f"verification: {record.verification}")

    if record.status in {"not_solved", "node_limit"}:
        return 2
    if record.verification != "passed":
        return 1
    return 0
