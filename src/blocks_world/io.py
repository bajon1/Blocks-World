from pathlib import Path

from .block_state import BlockState, validate_state
from .problem import BlocksProblem, Variant


def _parse_state(line: str, line_number: int) -> BlockState:
    try:
        state = BlockState(tuple(map(int, line.split())))
        validate_state(state)
        return state
    except ValueError as error:
        raise ValueError(f"Line {line_number}: {error}") from error


def read_problem(path: str | Path, variant: Variant) -> BlocksProblem:
    data_lines = [
        (line_number, line.strip())
        for line_number, line in enumerate(
            Path(path).read_text(encoding="utf-8").splitlines(),
            start=1,
        )
        if line.strip() and not line.lstrip().startswith("#")
    ]

    if len(data_lines) == 1 and data_lines[0][1].count(",") == 1:
        line_number, contents = data_lines[0]
        state_lines = [
            (line_number, part.strip())
            for part in contents.split(",")
        ]
    else:
        state_lines = data_lines

    if len(state_lines) != 2 or any(not line for _, line in state_lines):
        raise ValueError(
            "Input must contain exactly two states: start and goal"
        )

    start = _parse_state(state_lines[0][1], state_lines[0][0])
    goal = _parse_state(state_lines[1][1], state_lines[1][0])

    if len(start) != len(goal):
        raise ValueError("Start and goal must have the same size")

    return BlocksProblem(start=start, goal=goal, variant=variant)


def read_problems(path: str | Path, variant: Variant) -> list[BlocksProblem]:
    """Compatibility wrapper for callers expecting a collection."""
    return [read_problem(path, variant)]


def write_problem(path: str | Path, problem: BlocksProblem) -> None:
    contents = (
        f"{' '.join(map(str, problem.start.state))}\n"
        f"{' '.join(map(str, problem.goal.state))}\n"
    )
    Path(path).write_text(contents, encoding="utf-8")
