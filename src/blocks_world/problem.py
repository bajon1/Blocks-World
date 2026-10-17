from dataclasses import dataclass
from enum import Enum

from .block_state import BlocksState


class Variant(Enum):
    BASIC = "basic"
    EXTENDED = "extended"


@dataclass(frozen=True, slots=True)
class BlocksProblem:
    start: BlocksState
    goal: BlocksState
    variant: Variant