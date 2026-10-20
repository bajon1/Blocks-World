from collections.abc import Iterable
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


def _read_data_lines(path: str | Path) -> list[tuple[int, str]]:
    return [
        (line_number, line.strip())
        for line_number, line in enumerate(
            Path(path).read_text(encoding="utf-8").splitlines(),
            start=1,
        )
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _build_problem(
    state_lines: list[tuple[int, str]],
    variant: Variant,
) -> BlocksProblem:

    if len(state_lines) != 2 or any(not line for _, line in state_lines):
        raise ValueError(
            "Input must contain exactly two states: start and goal"
        )

    start = _parse_state(state_lines[0][1], state_lines[0][0])
    goal = _parse_state(state_lines[1][1], state_lines[1][0])

    if len(start) != len(goal):
        raise ValueError("Start and goal must have the same size")

    return BlocksProblem(start=start, goal=goal, variant=variant)


def read_problem(path: str | Path, variant: Variant) -> BlocksProblem:
    problems = read_problems(path, variant)
    if len(problems) != 1:
        raise ValueError("Input must contain exactly one problem")
    return problems[0]


def read_problems(path: str | Path, variant: Variant) -> list[BlocksProblem]:
    data_lines = _read_data_lines(path)
    if not data_lines:
        raise ValueError("Input must contain at least one problem")

    if all("," not in line for _, line in data_lines):
        if len(data_lines) != 2:
            raise ValueError(
                "Input must contain exactly two states: start and goal"
            )
        return [_build_problem(data_lines, variant)]

    problems = []
    for line_number, contents in data_lines:
        if contents.count(",") != 1:
            raise ValueError(
                f"Line {line_number}: each problem must contain "
                "start and goal separated by one comma"
            )
        state_lines = [
            (line_number, part.strip())
            for part in contents.split(",")
        ]
        problems.append(_build_problem(state_lines, variant))
    return problems


def write_problem(path: str | Path, problem: BlocksProblem) -> None:
    contents = (
        f"{' '.join(map(str, problem.start.state))}\n"
        f"{' '.join(map(str, problem.goal.state))}\n"
    )
    Path(path).write_text(contents, encoding="utf-8")


def write_problems(
    path: str | Path,
    problems: Iterable[BlocksProblem],
) -> None:
    lines = [
        f"{' '.join(map(str, problem.start.state))}, "
        f"{' '.join(map(str, problem.goal.state))}"
        for problem in problems
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
