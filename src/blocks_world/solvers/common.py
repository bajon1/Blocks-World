from collections.abc import Mapping

from ..block_state import BlockState
from ..moves import Move


def reconstruct_moves(
    parents: Mapping[BlockState, tuple[BlockState, Move]],
    goal: BlockState,
) -> list[Move]:
    moves: list[Move] = []
    state = goal

    while state in parents:
        state, move = parents[state]
        moves.append(move)

    moves.reverse()
    return moves
