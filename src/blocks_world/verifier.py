from .moves import Move, apply_move
from .problem import BlocksProblem, SearchResult, Variant


def verify_solution(problem: BlocksProblem, result: SearchResult) -> None:
    state = problem.start

    if result.n_moves != len(result.moves):
        raise ValueError("Number of moves does not match the move list")

    for i, move in enumerate(result.moves, start=1):
        block, destination = move
        n = len(state)

        if not 1 <= block <= n:
            raise ValueError(f"Move {i}: invalid block {block}")

        if not 0 <= destination <= n:
            raise ValueError(f"Move {i}: invalid destination {destination}")

        if block == destination:
            raise ValueError(f"Move {i}: block cannot be placed on itself")

        if block in state.state:
            raise ValueError(f"Move {i}: block {block} is not clear")

        if destination != 0 and destination in state.state:
            raise ValueError(
                f"Move {i}: destination block {destination} is not clear"
            )

        support = state.state[block - 1]

        if destination == support:
            raise ValueError(f"Move {i}: block is already at destination")

        if (
            problem.variant == Variant.BASIC
            and support != 0
            and destination != 0
        ):
            raise ValueError(
                f"Move {i}: moving between blocks is forbidden in BASIC"
            )

        state = apply_move(state, move)

    if state != problem.goal:
        raise ValueError("Final state does not match the goal")