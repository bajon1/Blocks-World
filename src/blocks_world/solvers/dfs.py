from __future__ import annotations

from ..block_state import BlockState
from ..moves import Move, apply_move, generate_moves  # noqa: F401
from ..problem import BlocksProblem, SearchResult  # noqa: F401

def dfs(problem: BlocksProblem,) -> SearchResult:

    start, goal, variant = problem.start, problem.goal, problem.variant

    if start == goal:
        return SearchResult([], 0, True)

    def untried_moves(state: BlockState):
        return iter(generate_moves(state, variant))

    visited : set[BlocksProblem] = set()
    states = [start]
    path : list[Move] = []
    stack = [untried_moves(start)]

    visited.add(start)

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
            return SearchResult(path, len(visited), True)

        states.append(new_state)
        stack.append(untried_moves(new_state))

    return SearchResult(stack, len(visited), False)