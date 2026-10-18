from typing import NamedTuple
from itertools import permutations

from .block_state import BlockState
from .problem import Variant

class Move(NamedTuple):
    block: int
    destination: int


def generate_moves(state: BlockState, variant: Variant) -> list[Move]:
    state_set = set(state.state)

    available_blocks = [
        block
        for block in range(1, len(state.state) + 1)
        if block not in state_set
    ]

    moves = []

    moves.extend(
        Move(block, 0)
        for block in available_blocks
        if state.state[block - 1] != 0
    )

    moves.extend(
        Move(block, destination)
        for block, destination in permutations(available_blocks, 2)
        if variant == Variant.EXTENDED or state.state[block - 1] == 0
    )

    return moves



def apply_move(state: BlockState, move: Move) -> BlockState:
    new_state = list(state.state)
    new_state[move.block - 1] = move.destination

    return BlockState(tuple(new_state))


