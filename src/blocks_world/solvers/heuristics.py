from __future__ import annotations

from collections.abc import Callable

from ..block_state import BlockState

Heuristic = Callable[[BlockState, BlockState], int]


def misplaced_blocks(state: BlockState, goal: BlockState) -> int:
    """Heuristic 1: number of blocks lying on a different support than in the goal.

    The support is either a block or the table. Admissible: a single move
    changes the support of exactly one block, so every misplaced block needs
    at least one move of its own.
    """
    return sum(
        1
        for support, goal_support in zip(state.state, goal.state)
        if support != goal_support
    )


def foundation_blocks(state: BlockState, goal: BlockState) -> int:
    """Heuristic 2: lower bound on the number of moves of every single block.

    A block is "in place" when its support equals the goal support and that
    support is in place too (the table always is). Cost of a block:
      0 - in place,
      1 - its support differs from the goal support (it has to be moved),
      2 - its support is the goal one, but that support is not in place.
          The support has to be moved at some point, so the block must first
          be taken off it and later put back on it.
    A move changes only one block, so the sum is a lower bound on the number
    of moves. It is never smaller than misplaced_blocks.
    """
    supports = state.state
    goal_supports = goal.state

    above = [0] * (len(supports) + 1)
    for block, support in enumerate(supports, start=1):
        if support != 0:
            above[support] = block

    in_place = [False] * (len(supports) + 1)
    in_place[0] = True
    total = 0

    # Walk every tower from the table upwards, so the support of a block is
    # always classified before the block itself.
    for bottom, bottom_support in enumerate(supports, start=1):
        if bottom_support != 0:
            continue

        block = bottom
        while block != 0:
            below = supports[block - 1]

            if below != goal_supports[block - 1]:
                total += 1
            elif in_place[below]:
                in_place[block] = True
            else:
                total += 2

            block = above[block]

    return total


HEURISTICS: dict[str, Heuristic] = {
    "misplaced": misplaced_blocks,
    "foundation": foundation_blocks,
}


def get_heuristic(name: str | None) -> Heuristic:
    try:
        return HEURISTICS[name]
    except KeyError:
        raise ValueError(
            f"Unknown heuristic {name!r}, available: {', '.join(HEURISTICS)}"
        ) from None