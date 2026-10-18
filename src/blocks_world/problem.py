from dataclasses import dataclass
from enum import Enum

from .block_state import BlocksState


class Variant(Enum):
    """ Choose a problem variant.

    Basic variant allows blocks to be moved only to and from the table.
    Extended variant also allows blocks to be moved from the top of one stack to another.
    """
    BASIC = "basic"
    EXTENDED = "extended"


@dataclass(frozen=True, slots=True)
class BlocksProblem:
    """Definition of a Blocks World problem.

    Start state
    Goal state
    Problem variant
    """
    start: BlocksState
    goal: BlocksState
    variant: Variant