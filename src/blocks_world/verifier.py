from .moves import Move, apply_move
from .problem import BlocksProblem, SearchResult, Variant


class SolutionVerificationError(ValueError):
    def __init__(self, message: str, move_number: int | None = None):
        super().__init__(message)
        self.move_number = move_number


def _invalid_move(move_number: int, reason: str) -> None:
    raise SolutionVerificationError(
        f"Move {move_number}: {reason}",
        move_number=move_number,
    )


def verify_solution(problem: BlocksProblem, result: SearchResult) -> None:
    if not result.is_solved:
        raise SolutionVerificationError("Search result is not solved")

    state = problem.start

    for i, move in enumerate(result.moves, start=1):
        try:
            block, destination = move
        except (TypeError, ValueError):
            _invalid_move(i, "move must contain exactly two integers")

        if (
            not isinstance(block, int)
            or isinstance(block, bool)
            or not isinstance(destination, int)
            or isinstance(destination, bool)
        ):
            _invalid_move(i, "move must contain exactly two integers")

        n = len(state)

        if not 1 <= block <= n:
            _invalid_move(i, f"invalid block {block}")

        if not 0 <= destination <= n:
            _invalid_move(i, f"invalid destination {destination}")

        if block == destination:
            _invalid_move(i, "block cannot be placed on itself")

        if block in state.state:
            _invalid_move(i, f"block {block} is not clear")

        if destination != 0 and destination in state.state:
            _invalid_move(i, f"destination block {destination} is not clear")

        support = state.state[block - 1]

        if destination == support:
            _invalid_move(i, "block is already at destination")

        if (
            problem.variant == Variant.BASIC
            and support != 0
            and destination != 0
        ):
            _invalid_move(i, "moving between blocks is forbidden in BASIC")

        state = apply_move(state, move)

    if state != problem.goal:
        raise SolutionVerificationError("Final state does not match the goal")
