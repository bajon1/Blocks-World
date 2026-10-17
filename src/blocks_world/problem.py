from dataclasses import dataclass
from enum import Enum

from .block_state import BlockState


class Variant(Enum):
    BASIC = "basic"
    EXTENDED = "extended"


@dataclass(frozen=True, slots=True)
class BlocksProblem:
    start: BlockState
    goal: BlockState
    variant: Variant
