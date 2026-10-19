import pytest

from blocks_world.block_state import BlockState
from blocks_world.moves import Move
from blocks_world.problem import (
    BlocksProblem,
    SearchResult,
    Variant,
)
from blocks_world.verifier import SolutionVerificationError, verify_solution


def result(*moves: Move, is_solved: bool = True):
    return SearchResult(
        moves=list(moves),
        visited=1,
        is_solved=is_solved,
    )


def test_verify_solution_accepts_valid_sequence():
    problem = BlocksProblem(
        start=BlockState((0, 1, 0)),
        goal=BlockState((0, 0, 0)),
        variant=Variant.BASIC,
    )

    assert verify_solution(problem, result(Move(2, 0))) is None


def test_verify_solution_reports_first_invalid_move_number():
    problem = BlocksProblem(
        start=BlockState((0, 1, 0)),
        goal=BlockState((0, 0, 0)),
        variant=Variant.BASIC,
    )

    with pytest.raises(SolutionVerificationError, match="Move 1.*not clear") as error:
        verify_solution(problem, result(Move(1, 3), Move(2, 0)))

    assert error.value.move_number == 1


def test_verify_solution_enforces_basic_variant():
    problem = BlocksProblem(
        start=BlockState((0, 1, 0, 3)),
        goal=BlockState((0, 4, 0, 3)),
        variant=Variant.BASIC,
    )

    with pytest.raises(SolutionVerificationError, match="Move 1.*BASIC"):
        verify_solution(problem, result(Move(2, 4)))


def test_verify_solution_reports_wrong_final_state():
    problem = BlocksProblem(
        start=BlockState((0, 1, 0)),
        goal=BlockState((0, 0, 0)),
        variant=Variant.BASIC,
    )

    with pytest.raises(SolutionVerificationError, match="Final state") as error:
        verify_solution(problem, result())

    assert error.value.move_number is None


def test_verify_solution_rejects_unsolved_search_result():
    problem = BlocksProblem(
        start=BlockState((0, 0)),
        goal=BlockState((0, 0)),
        variant=Variant.BASIC,
    )

    with pytest.raises(SolutionVerificationError, match="not solved"):
        verify_solution(problem, result(is_solved=False))


@pytest.mark.parametrize(
    ("move", "message"),
    [
        ((1,), "exactly two integers"),
        ((1, 0, 2), "exactly two integers"),
        (("1", 0), "exactly two integers"),
        ((True, 0), "exactly two integers"),
    ],
)
def test_verify_solution_reports_malformed_move_as_first_invalid_move(
    move,
    message,
):
    problem = BlocksProblem(
        start=BlockState((0, 0)),
        goal=BlockState((0, 0)),
        variant=Variant.EXTENDED,
    )
    malformed = SearchResult(moves=[move], visited=1, is_solved=True)

    with pytest.raises(SolutionVerificationError, match=f"Move 1.*{message}") as error:
        verify_solution(problem, malformed)

    assert error.value.move_number == 1
