from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from .block_state import BlockState

if TYPE_CHECKING:
    from .moves import Move


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
    start: BlockState
    goal: BlockState
    variant: Variant

@dataclass(slots=True)
class SearchResult:
    """Results of a search.
    moves: list[Move] - list of done moves
    n_moves: int - number of moves
    """
    moves: list[Move]
    n_moves: int
