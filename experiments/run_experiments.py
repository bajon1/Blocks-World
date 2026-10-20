import argparse
from collections.abc import Sequence
from pathlib import Path

from blocks_world.cli import load_solver
from utils.experiments import run_standard_experiments, write_results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run all experiments required for the 8-point report"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data/generated/seed_42/base.txt"),
    )
    parser.add_argument(
        "--n8-dir",
        type=Path,
        default=Path("data/generated/seed_42/n8_extended.txt"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/results.json"),
    )
    parser.add_argument(
        "--first-heuristic",
        default="misplaced",
    )
    parser.add_argument("--second-heuristic", required=True)
    parser.add_argument("--max-expanded", type=int, default=1_000_000)
    args = parser.parse_args(argv)

    if args.max_expanded < 1:
        parser.error("max-expanded must be positive")

    completed = []

    def save_progress(record):
        completed.append(record)
        write_results(args.output, completed)
        print(
            f"[{len(completed):3d}/135] {record.algorithm} "
            f"{record.case_id}: {record.status}",
            flush=True,
        )

    records = run_standard_experiments(
        base_dir=args.base_dir,
        n8_dir=args.n8_dir,
        solver_loader=load_solver,
        first_heuristic=args.first_heuristic,
        second_heuristic=args.second_heuristic,
        max_expanded=args.max_expanded,
        on_record=save_progress,
    )
    write_results(args.output, records)

    print(f"Saved {len(records)} experiment records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
