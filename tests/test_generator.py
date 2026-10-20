import random
from pathlib import Path

import pytest

from blocks_world.block_state import validate_state
from blocks_world.generator import generate_dataset, generate_problems
from blocks_world.io import read_problems
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
                output_path="tests/unused-generator-output.txt",
            seed=42,
            count_per_n=1,
            min_blocks=minimum,
            max_blocks=maximum,
            variant=Variant.BASIC,
        )


def test_generate_dataset_writes_one_collection_file():
    output_path = Path("tests/_runtime_problems.txt")

    try:
        problems = generate_dataset(
            output_path=output_path,
            seed=42,
            count_per_n=2,
            min_blocks=3,
            max_blocks=4,
            variant=Variant.BASIC,
        )

        assert len(problems) == 4
        assert output_path.exists()
        assert len(output_path.read_text(encoding="utf-8").splitlines()) == 4
        assert read_problems(output_path, Variant.BASIC) == problems
    finally:
        output_path.unlink(missing_ok=True)
