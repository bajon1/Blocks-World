import pytest

from dataclasses import FrozenInstanceError

from blocks_world.block_state import BlockState
from blocks_world.problem import BlocksProblem, Variant


def test_problem_creation():
    start = BlockState((0, 1, 0))
    goal = BlockState((0, 0, 2))

    problem = BlocksProblem(
        start=start,
        goal=goal,
        variant=Variant.BASIC,
    )

    assert problem.start == start
    assert problem.goal == goal
    assert problem.variant == Variant.BASIC


def test_problem_extended_variant():
    problem = BlocksProblem(
        start=BlockState((0, 1, 0)),
        goal=BlockState((0, 0, 2)),
        variant=Variant.EXTENDED,
    )

    assert problem.variant == Variant.EXTENDED


def test_problem_immutable():
    problem = BlocksProblem(
        start=BlockState((0, 1, 0)),
        goal=BlockState((0, 0, 2)),
        variant=Variant.BASIC,
    )

    with pytest.raises(FrozenInstanceError):
        problem.variant = Variant.EXTENDED