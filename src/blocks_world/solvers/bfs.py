from __future__ import annotations

from collections import deque

from ..block_state import BlockState
from ..moves import Move, apply_move, generate_moves
from ..problem import BlocksProblem, SearchResult


def bfs(problem: BlocksProblem,
        *, max_expanded: int = 1_000_000,
        ) -> SearchResult:

    if max_expanded < 1:
        raise ValueError("max_expanded must be positive")

    start, goal, variant = problem.start, problem.goal, problem.variant
    if start == goal:
        return SearchResult(moves=[], visited=0, is_solved=True)

    parents: dict[BlockState, tuple[BlockState, Move] | None] = {start: None}
    queue = deque([start])
    expanded = 0

    while queue:
        if expanded >= max_expanded:
            return SearchResult(moves=[], visited=expanded, is_solved=False)

        state = queue.popleft()
        expanded += 1

        for move in generate_moves(state, variant):
            new_state = apply_move(state, move)
            if new_state in parents:
                continue

            parents[new_state] = (state, move)

            if new_state == goal:
                return SearchResult(
                    moves=_path_to(goal, parents),
                    visited=expanded,
                    is_solved=True,
                )

            queue.append(new_state)

    return SearchResult(moves=[], visited=expanded, is_solved=False)


def _path_to(
        state: BlockState,
        parents: dict[BlockState, tuple[BlockState, Move] | None],
        ) -> list[Move]:
    moves: list[Move] = []

    while parents[state] is not None:
        state, move = parents[state]
        moves.append(move)

    moves.reverse()
    return moves