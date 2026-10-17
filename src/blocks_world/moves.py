from typing import NamedTuple

from .block_state import BlockState

class Move(NamedTuple):
    block: int
    destination: int

def generate_moves(state: BlockState) -> list[Move]:
    pass

def apply_moves(state: BlockState, move: Move) -> BlockState:
    pass


