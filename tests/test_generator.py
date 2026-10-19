import random
from pathlib import Path

import pytest

from blocks_world.block_state import validate_state
from blocks_world.generator import generate_dataset, generate_problems
from blocks_world.io import read_problem
from blocks_world.problem import Variant


def test_generate_problems_is_reproducible():
    first = generate_problems(8, 5, random.Random(42))
    second = generate_problems(8, 5, random.Random(42))

    assert first == second


def test_generate_problems_are_distinct_and_nontrivial():
    problems = generate_problems(3, 10, random.Random(0))

    assert len(problems) == 10
    assert len(set(problems)) == 10
    assert all(start != goal for start, goal in problems)


def test_generate_problems_contain_valid_states():
    for start, goal in generate_problems(15, 5, random.Random(42)):
        assert validate_state(start) is None
        assert validate_state(goal) is None


def test_generate_problems_rejects_fewer_than_three_blocks():
    with pytest.raises(ValueError, match="at least 3"):
        generate_problems(2, 5, random.Random(42))


def test_generate_problems_rejects_more_pairs_than_exist():
    with pytest.raises(ValueError, match="at most 156"):
        generate_problems(3, 157, random.Random(42))


@pytest.mark.parametrize("count", [0, -1])
def test_generate_problems_rejects_nonpositive_count(count):
    with pytest.raises(ValueError, match="positive"):
        generate_problems(3, count, random.Random(42))


@pytest.mark.parametrize(
    ("minimum", "maximum", "message"),
    [(2, 3, "at least 3"), (5, 4, "not be smaller")],
)
def test_generate_dataset_rejects_invalid_range(minimum, maximum, message):
    with pytest.raises(ValueError, match=message):
        generate_dataset(
            output_dir="tests/unused-generator-output",
            seed=42,
            count_per_n=1,
            min_blocks=minimum,
            max_blocks=maximum,
            variant=Variant.BASIC,
        )


def test_generate_dataset_writes_spec_format_files():
    output_dir = Path("tests")
    expected_paths = [
        output_dir / "problem_n03_01.txt",
        output_dir / "problem_n03_02.txt",
        output_dir / "problem_n04_01.txt",
        output_dir / "problem_n04_02.txt",
    ]

    try:
        paths = generate_dataset(
            output_dir=output_dir,
            seed=42,
            count_per_n=2,
            min_blocks=3,
            max_blocks=4,
            variant=Variant.BASIC,
        )

        assert paths == expected_paths
        assert all(path.exists() for path in paths)
        assert all(
            read_problem(path, Variant.BASIC).start
            != read_problem(path, Variant.BASIC).goal
            for path in paths
        )
    finally:
        for path in expected_paths:
            path.unlink(missing_ok=True)
