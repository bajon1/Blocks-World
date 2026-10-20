from pathlib import Path

import pytest

from blocks_world.block_state import BlockState
from blocks_world.io import (
    read_problem,
    read_problems,
    write_problem,
    write_problems,
)
from blocks_world.problem import BlocksProblem, Variant


@pytest.fixture
def problem_path():
    path = Path("tests/_runtime_problem.txt")
    yield path
    path.unlink(missing_ok=True)


def test_read_problem_ignores_comments_and_blank_lines(problem_path: Path):
    path = problem_path
    path.write_text(
        "# start\n\n0 1 0 2 3\n# goal\n2 3 4 5 0\n",
        encoding="utf-8",
    )

    problem = read_problem(path, Variant.BASIC)

    assert problem == BlocksProblem(
        start=BlockState((0, 1, 0, 2, 3)),
        goal=BlockState((2, 3, 4, 5, 0)),
        variant=Variant.BASIC,
    )


def test_read_problem_accepts_original_comma_separated_format(problem_path: Path):
    problem_path.write_text(
        "0 1 0 2 3, 2 3 4 5 0\n",
        encoding="utf-8",
    )

    problem = read_problem(problem_path, Variant.BASIC)

    assert problem == BlocksProblem(
        start=BlockState((0, 1, 0, 2, 3)),
        goal=BlockState((2, 3, 4, 5, 0)),
        variant=Variant.BASIC,
    )

@pytest.mark.parametrize(
    "contents, message",
    [
        ("0 0 0\n", "exactly two"),
        ("0 0 0\n0 0 0\n0 0 0\n", "exactly two"),
        ("0 0\n0 0 0\n", "same size"),
        ("0 x 0\n0 0 0\n", "Line 1"),
        ("0 1 1\n0 0 0\n", "Line 1"),
        ("1 0\n0 0\n", "itself"),
        ("3 0\n0 0\n", "Invalid support"),
        ("0 1 1\n0 0 0\n", "Multiple blocks"),
        ("2 1\n0 0\n", "Cycle"),
    ],
)
def test_read_problem_rejects_invalid_input(
    problem_path: Path,
    contents: str,
    message: str,
):
    path = problem_path
    path.write_text(contents, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        read_problem(path, Variant.BASIC)


def test_write_problem_round_trip(problem_path: Path):
    original = BlocksProblem(
        start=BlockState((0, 1, 0)),
        goal=BlockState((2, 0, 0)),
        variant=Variant.EXTENDED,
    )
    path = problem_path

    write_problem(path, original)

    assert path.read_text(encoding="utf-8") == "0 1 0\n2 0 0\n"
    assert read_problem(path, Variant.EXTENDED) == original


def test_read_problems_keeps_single_file_compatibility(problem_path: Path):
    problem_path.write_text("0 1 0\n0 0 2\n", encoding="utf-8")

    problems = read_problems(problem_path, Variant.BASIC)

    assert problems == [
        BlocksProblem(
            start=BlockState((0, 1, 0)),
            goal=BlockState((0, 0, 2)),
            variant=Variant.BASIC,
        )
    ]


def test_problem_collection_uses_one_comma_separated_case_per_line(
    problem_path: Path,
):
    problem_path.write_text(
        "2 0 0, 3 0 0\n"
        "0 0 0, 0 0 2\n",
        encoding="utf-8",
    )

    problems = read_problems(problem_path, Variant.BASIC)

    assert problems == [
        BlocksProblem(
            start=BlockState((2, 0, 0)),
            goal=BlockState((3, 0, 0)),
            variant=Variant.BASIC,
        ),
        BlocksProblem(
            start=BlockState((0, 0, 0)),
            goal=BlockState((0, 0, 2)),
            variant=Variant.BASIC,
        ),
    ]


def test_write_problems_writes_all_cases_to_one_file(problem_path: Path):
    problems = [
        BlocksProblem(
            start=BlockState((2, 0, 0)),
            goal=BlockState((3, 0, 0)),
            variant=Variant.BASIC,
        ),
        BlocksProblem(
            start=BlockState((0, 0, 0)),
            goal=BlockState((0, 0, 2)),
            variant=Variant.BASIC,
        ),
    ]

    write_problems(problem_path, problems)

    assert problem_path.read_text(encoding="utf-8") == (
        "2 0 0, 3 0 0\n"
        "0 0 0, 0 0 2\n"
    )
