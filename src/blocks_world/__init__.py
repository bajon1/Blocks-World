from pathlib import Path
import argparse
import random

from .generator import generate_problems
from .block_state import BlockState
from .problem import BlocksProblem, Variant


def problems() -> None:
    parser = argparse.ArgumentParser(description="Read Blocks World problems")

    parser.add_argument("path", type=Path)
    parser.add_argument(
        "variant",
        type=Variant,
        choices=list(Variant),
    )

    args = parser.parse_args()

    for line in args.path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        start, goal = line.split(",", maxsplit=1)

        problem = BlocksProblem(
            start=BlockState(tuple(map(int, start.split()))),
            goal=BlockState(tuple(map(int, goal.split()))),
            variant=args.variant,
        )

        print(problem)

def generate() -> None:
    parser = argparse.ArgumentParser(description="Generate Blocks World problems")

    parser.add_argument(
        "-n", "--number",
        type=int,
        default=5,
        help="Number of problems per block count (default: 5)",
    )
    parser.add_argument(
        "-r", "--random-state",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )

    args = parser.parse_args()

    if args.number < 1:
        parser.error("Number must be positive")

    rng = random.Random(args.random_state)

    output = Path("data") / f"_data_{args.random_state}.txt"
    output.parent.mkdir(parents=True, exist_ok=True)

    lines = []

    for n in range(3, 16):
        for start, goal in generate_problems(n, args.number, rng):
            lines.append(
                f"{' '.join(map(str, start.state))}, "
                f"{' '.join(map(str, goal.state))}"
            )

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Generated {len(lines)} problems")
    print(f"Saved to: {output}")

def solve() -> None:
    pass