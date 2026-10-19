from __future__ import annotations

import sys

from ..block_state import BlockState
from ..moves import Move, apply_move, generate_moves
from ..problem import BlocksProblem, SearchResult
from .heuristics import get_heuristic

# Return codes of one depth-first pass. Any value >= 0 is the next threshold.
FOUND = -1
LIMIT = -2
NO_BOUND = sys.maxsize


def ida_star(problem: BlocksProblem,
             *, max_expanded: int = 1_000_000,
             heuristic: str = "misplaced",
             ) -> SearchResult:
    """Iterative deepening A*: depth-first search limited by f = g + h.

    g - number of moves made so far, h - admissible estimate of the moves left.
    Every pass explores only states with f <= threshold; the next threshold is
    the smallest f that was cut off. With an admissible h the first solution
    found is the shortest one. Expanded nodes are summed over all passes.
    """
    if max_expanded < 1:
        raise ValueError("max_expanded must be positive")

    h = get_heuristic(heuristic)
    start, goal, variant = problem.start, problem.goal, problem.variant
    if start == goal:
        return SearchResult(moves=[], visited=0, is_solved=True)

    # Any state can be turned into any other one with at most 2n - 2 moves
    # (put every tower on the table, then build the goal), so the threshold
    # of an admissible heuristic never exceeds it.
    max_threshold = 2 * len(start) - 2

    expanded = 0
    path: list[Move] = []
    on_path: set[BlockState] = {start}

    def search(state: BlockState, g: int, threshold: int) -> int:
        nonlocal expanded

        if expanded >= max_expanded:
            return LIMIT
        expanded += 1

        next_threshold = NO_BOUND

        for move in generate_moves(state, variant):
            new_state = apply_move(state, move)
            if new_state in on_path:
                continue

            f = g + 1 + h(new_state, goal)
            if f > threshold:
                next_threshold = min(next_threshold, f)
                continue

            path.append(move)
            if new_state == goal:
                return FOUND

            on_path.add(new_state)
            result = search(new_state, g + 1, threshold)
            if result < 0:
                return result

            on_path.remove(new_state)
            path.pop()
            next_threshold = min(next_threshold, result)

        return next_threshold

    threshold = h(start, goal)
    while threshold <= max_threshold:
        result = search(start, 0, threshold)

        if result == FOUND:
            return SearchResult(
                moves=list(path),
                visited=expanded,
                is_solved=True,
            )
        if result == LIMIT:
            return SearchResult(moves=[], visited=expanded, is_solved=False)

        threshold = result

    return SearchResult(moves=[], visited=expanded, is_solved=False)