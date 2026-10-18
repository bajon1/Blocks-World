from pathlib import Path

from .block_state import BlockState, validate_state
from .problem import BlocksProblem, Variant


def read_problems(path: str | Path, variant: Variant) -> list[BlocksProblem]:
    problems = []

    for i, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue

        try:
            start, goal = line.split(",", maxsplit=1)

            start = BlockState(tuple(map(int, start.split())))
            goal = BlockState(tuple(map(int, goal.split())))

            validate_state(start)
            validate_state(goal)

            if len(start) != len(goal):
                raise ValueError("Start and goal must have the same size")

            problems.append(BlocksProblem(start, goal, variant))

        except ValueError as error:
            raise ValueError(f"Line {i}: {error}") from error

    return problems