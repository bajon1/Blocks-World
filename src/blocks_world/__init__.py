import sys
from pathlib import Path

from .block_state import BlockState
from .problem import BlocksProblem, Variant


def problems() -> None:
    path, variant = sys.argv[1:]

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        start, goal = line.split(",", maxsplit=1)
        problem = BlocksProblem(
            start=BlockState(tuple(map(int, start.split()))),
            goal=BlockState(tuple(map(int, goal.split()))),
            variant=Variant(variant),
        )
        print(problem)


def solve() -> None:
    pass