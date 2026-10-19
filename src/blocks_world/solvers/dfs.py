from __future__ import annotations

from collections.abc import Iterator

from ..block_state import BlockState
from ..moves import Move, apply_move, generate_moves
from ..problem import BlocksProblem, SearchResult


def dfs(problem: BlocksProblem,
        *, max_expanded: int = 1_000_000,
        ) -> SearchResult:

    if max_expanded < 1:
        raise ValueError("max_expanded must be positive")

    start, goal, variant = problem.start, problem.goal, problem.variant
    if start == goal:
        return SearchResult(moves=[], visited=0, is_solved=True)

    def untried_moves(state: BlockState) -> Iterator[Move]:
        return iter(generate_moves(state, variant))

    visited: set[BlockState] = {start}
    states = [start]
    path: list[Move] = []
    stack = [untried_moves(start)]
    expanded = 1

    while stack:
        move = next(stack[-1], None)
        if move is None:
            stack.pop()
            states.pop()
            if path:
                path.pop()
            continue

        new_state = apply_move(states[-1], move)
        if new_state in visited:
            continue

        visited.add(new_state)
        path.append(move)

        if new_state == goal:
            return SearchResult(
                moves=list(path),
                visited=expanded,
                is_solved=True,
            )

        if expanded >= max_expanded:
            return SearchResult(moves=[], visited=expanded, is_solved=False)

        expanded += 1
        states.append(new_state)
        stack.append(untried_moves(new_state))

    return SearchResult(moves=[], visited=expanded, is_solved=False)
