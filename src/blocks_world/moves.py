from collections.abc import Iterator
from typing import NamedTuple
from itertools import permutations

from .block_state import BlockState
from .problem import Variant

class Move(NamedTuple):
    block: int
    destination: int


def iter_moves(state: BlockState, variant: Variant) -> Iterator[Move]:
    state_set = set(state.state)

    available_blocks = [
        block
        for block in range(1, len(state.state) + 1)
        if block not in state_set
    ]

    yield from (
        Move(block=block, destination=0)
        for block in available_blocks
        if state.state[block - 1] != 0
    )

    yield from (
        Move(block=block, destination=destination)
        for block, destination in permutations(available_blocks, 2)
        if variant == Variant.EXTENDED or state.state[block - 1] == 0
    )


def generate_moves(state: BlockState, variant: Variant) -> list[Move]:
    return list(iter_moves(state, variant))



def apply_move(state: BlockState, move: Move) -> BlockState:
    new_state = list(state.state)
    new_state[move.block - 1] = move.destination

    return BlockState(tuple(new_state))


